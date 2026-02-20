"""
Customer & Quotation Repository
Data access layer for Customer, Quotation, QuotationItem, and related entities.
"""

from sqlalchemy.orm import Session, joinedload, selectinload
from typing import List, Optional
from datetime import datetime

from app.models import (
    Customer, Quotation, QuotationItem,
    QuotationItemService, QuotationItemServiceUnitValue,
    Service, ServiceOption, DoorTypeThicknessOption,
)
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.schemas.quotation import (
    QuotationCreate, QuotationUpdate,
    QuotationItemCreate, QuotationItemUpdate,
    QuotationItemServiceCreate, QuotationItemServiceUpdate,
)


class CustomerQuotationRepository:

    # ========================================================================
    # CUSTOMER
    # ========================================================================

    @staticmethod
    def create_customer(db: Session, data: CustomerCreate, username: str = None) -> Customer:
        customer = Customer(
            **data.model_dump(),
            created_by=username or "system",
            updated_by=username or "system",
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer

    @staticmethod
    def get_customer_by_id(db: Session, customer_id: int) -> Optional[Customer]:
        return db.query(Customer).filter(Customer.id == customer_id).first()

    @staticmethod
    def get_all_customers(db: Session, skip: int = 0, limit: int = 100) -> List[Customer]:
        return db.query(Customer).offset(skip).limit(limit).all()

    @staticmethod
    def count_customers(db: Session) -> int:
        return db.query(Customer).count()

    @staticmethod
    def update_customer(db: Session, customer_id: int, data: CustomerUpdate, username: str = None) -> Optional[Customer]:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(customer, key, value)
        if username:
            customer.updated_by = username
        db.commit()
        db.refresh(customer)
        return customer

    @staticmethod
    def delete_customer(db: Session, customer_id: int) -> bool:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return False
        db.delete(customer)
        db.commit()
        return True

    # ========================================================================
    # QUOTATION
    # ========================================================================

    @staticmethod
    def _calculate_service_cost(
        db: Session,
        svc_data: QuotationItemServiceCreate,
    ) -> float:
        """Calculate cost for a single quotation item service."""
        service = db.query(Service).filter(Service.id == svc_data.service_id).first()
        if not service:
            return 0.0

        cost = 0.0
        stype = service.service_type

        if stype == 'consumable':
            # rate × quantity; option cost overrides service.cost
            rate = service.cost or 0.0
            if svc_data.option_id:
                option = db.query(ServiceOption).filter(ServiceOption.id == svc_data.option_id).first()
                if option:
                    rate = option.cost or 0.0
            quantity = svc_data.quantity or 0.0
            cost = rate * quantity

        elif stype == 'add_on':
            # fixed cost from option or service.cost
            if svc_data.option_id:
                option = db.query(ServiceOption).filter(ServiceOption.id == svc_data.option_id).first()
                if option:
                    cost = option.cost or 0.0
            else:
                cost = service.cost or 0.0

        elif stype == 'labour':
            cost = svc_data.direct_amount or 0.0

        elif stype == 'grouping':
            # Grouping cost = sum of children costs (computed by parent)
            cost = 0.0

        # Double for both_sides
        if svc_data.both_sides and stype in ('consumable', 'add_on'):
            cost *= 2

        return round(cost, 2)

    @staticmethod
    def _calculate_item_costs(
        db: Session,
        item: QuotationItem,
        thickness_option: DoorTypeThicknessOption,
    ):
        """Calculate and set cost breakdown fields on a QuotationItem."""
        # Base cost = area × cost_per_sqft × quantity
        area = item.length * item.breadth
        item.base_cost = round(area * thickness_option.cost_per_sqft * item.quantity, 2)

        # Services cost = sum of all service costs
        total_services = 0.0
        for svc in item.services:
            total_services += svc.cost or 0
        item.services_cost = round(total_services, 2)

        # Linear cost flow
        item.subtotal = round(item.base_cost + item.services_cost, 2)
        item.total_after_discount = round(item.subtotal - (item.discount or 0), 2)
        item.tax_amount = round(item.total_after_discount * ((item.tax_percent or 0) / 100), 2)
        item.total = round(item.total_after_discount + item.tax_amount, 2)

    @staticmethod
    def create_quotation(db: Session, data: QuotationCreate, username: str = None) -> Quotation:
        """Create a quotation with items and services, computing all costs."""
        quotation_number = CustomerQuotationRepository.generate_quotation_number(db)

        quotation = Quotation(
            customer_id=data.customer_id,
            date=data.date,
            status=data.status or 'draft',
            quotation_number=quotation_number,
            notes=data.notes,
            total=0,
            created_by=username or "system",
            updated_by=username or "system",
        )
        db.add(quotation)
        db.flush()

        quotation_total = 0.0

        if data.items:
            for item_data in data.items:
                # Get thickness option for base cost
                thickness_option = db.query(DoorTypeThicknessOption).filter(
                    DoorTypeThicknessOption.id == item_data.thickness_option_id
                ).first()
                if not thickness_option:
                    raise ValueError(f"Thickness option {item_data.thickness_option_id} not found")

                item = QuotationItem(
                    quotation_id=quotation.id,
                    door_type_id=item_data.door_type_id,
                    thickness_option_id=item_data.thickness_option_id,
                    length=item_data.length,
                    breadth=item_data.breadth,
                    quantity=item_data.quantity or 1,
                    tax_percent=item_data.tax_percent or 0,
                    discount=item_data.discount or 0,
                    created_by=username or "system",
                    updated_by=username or "system",
                )
                db.add(item)
                db.flush()

                # Process services
                if item_data.services:
                    for svc_data in item_data.services:
                        cost = CustomerQuotationRepository._calculate_service_cost(db, svc_data)

                        svc = QuotationItemService(
                            quotation_item_id=item.id,
                            service_id=svc_data.service_id,
                            parent_id=svc_data.parent_id,
                            option_id=svc_data.option_id,
                            quantity=svc_data.quantity,
                            direct_amount=svc_data.direct_amount,
                            both_sides=svc_data.both_sides,
                            cost=cost,
                            created_by=username or "system",
                            updated_by=username or "system",
                        )
                        db.add(svc)
                        db.flush()

                        # Unit values
                        if svc_data.unit_values:
                            for uv_data in svc_data.unit_values:
                                uv = QuotationItemServiceUnitValue(
                                    quotation_item_service_id=svc.id,
                                    unit_id=uv_data.unit_id,
                                    value1=uv_data.value1,
                                    value2=uv_data.value2,
                                )
                                db.add(uv)

                    db.flush()

                # Refresh to get services list
                db.refresh(item)

                # Calculate item costs
                CustomerQuotationRepository._calculate_item_costs(db, item, thickness_option)
                quotation_total += item.total

        quotation.total = round(quotation_total, 2)
        db.commit()

        # Reload with relationships
        return CustomerQuotationRepository.get_quotation_by_id(db, quotation.id)

    @staticmethod
    def get_quotation_by_id(db: Session, quotation_id: int) -> Optional[Quotation]:
        return db.query(Quotation).options(
            selectinload(Quotation.customer),
            selectinload(Quotation.items)
                .selectinload(QuotationItem.door_type),
            selectinload(Quotation.items)
                .selectinload(QuotationItem.thickness_option),
            selectinload(Quotation.items)
                .selectinload(QuotationItem.services)
                .selectinload(QuotationItemService.service),
            selectinload(Quotation.items)
                .selectinload(QuotationItem.services)
                .selectinload(QuotationItemService.selected_option),
            selectinload(Quotation.items)
                .selectinload(QuotationItem.services)
                .selectinload(QuotationItemService.unit_values)
                .selectinload(QuotationItemServiceUnitValue.unit),
        ).filter(Quotation.id == quotation_id).first()

    @staticmethod
    def get_quotation_by_number(db: Session, quotation_number: str) -> Optional[Quotation]:
        return db.query(Quotation).options(
            selectinload(Quotation.customer),
            selectinload(Quotation.items)
                .selectinload(QuotationItem.door_type),
            selectinload(Quotation.items)
                .selectinload(QuotationItem.thickness_option),
            selectinload(Quotation.items)
                .selectinload(QuotationItem.services)
                .selectinload(QuotationItemService.service),
            selectinload(Quotation.items)
                .selectinload(QuotationItem.services)
                .selectinload(QuotationItemService.selected_option),
        ).filter(Quotation.quotation_number == quotation_number).first()

    @staticmethod
    def get_quotations_by_customer(db: Session, customer_id: int) -> List[Quotation]:
        return db.query(Quotation).options(
            selectinload(Quotation.customer),
        ).filter(Quotation.customer_id == customer_id).all()

    @staticmethod
    def get_all_quotations(db: Session, skip: int = 0, limit: int = 100) -> List[Quotation]:
        return db.query(Quotation).options(
            selectinload(Quotation.customer),
        ).order_by(Quotation.id.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def count_quotations(db: Session) -> int:
        return db.query(Quotation).count()

    @staticmethod
    def recalculate_quotation_costs(db: Session, quotation_id: int) -> Optional[Quotation]:
        """Recalculate all costs for a quotation from stored service costs."""
        quotation = db.query(Quotation).options(
            selectinload(Quotation.items).selectinload(QuotationItem.services),
            selectinload(Quotation.items).selectinload(QuotationItem.thickness_option),
        ).filter(Quotation.id == quotation_id).first()

        if not quotation:
            return None

        quotation_total = 0.0
        for item in quotation.items:
            CustomerQuotationRepository._calculate_item_costs(db, item, item.thickness_option)
            quotation_total += item.total

        quotation.total = round(quotation_total, 2)
        db.commit()
        return CustomerQuotationRepository.get_quotation_by_id(db, quotation_id)

    @staticmethod
    def update_quotation(db: Session, quotation_id: int, data: QuotationUpdate, updated_by: str = None) -> Optional[Quotation]:
        quotation = db.query(Quotation).filter(Quotation.id == quotation_id).first()
        if not quotation:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(quotation, key, value)
        if updated_by:
            quotation.updated_by = updated_by
        db.commit()
        db.refresh(quotation)
        return quotation

    @staticmethod
    def delete_quotation(db: Session, quotation_id: int) -> bool:
        quotation = db.query(Quotation).filter(Quotation.id == quotation_id).first()
        if not quotation:
            return False
        db.delete(quotation)
        db.commit()
        return True

    # ========================================================================
    # QUOTATION ITEM
    # ========================================================================

    @staticmethod
    def create_quotation_item(db: Session, data: QuotationItemCreate, created_by: str = None) -> QuotationItem:
        item = QuotationItem(
            quotation_id=data.quotation_id,
            door_type_id=data.door_type_id,
            thickness_option_id=data.thickness_option_id,
            length=data.length,
            breadth=data.breadth,
            quantity=data.quantity or 1,
            tax_percent=data.tax_percent or 0,
            discount=data.discount or 0,
            created_by=created_by or "system",
            updated_by=created_by or "system",
        )
        db.add(item)
        db.flush()

        thickness_option = db.query(DoorTypeThicknessOption).filter(
            DoorTypeThicknessOption.id == data.thickness_option_id
        ).first()

        if data.services:
            for svc_data in data.services:
                cost = CustomerQuotationRepository._calculate_service_cost(db, svc_data)
                svc = QuotationItemService(
                    quotation_item_id=item.id,
                    service_id=svc_data.service_id,
                    parent_id=svc_data.parent_id,
                    option_id=svc_data.option_id,
                    quantity=svc_data.quantity,
                    direct_amount=svc_data.direct_amount,
                    both_sides=svc_data.both_sides,
                    cost=cost,
                    created_by=created_by or "system",
                    updated_by=created_by or "system",
                )
                db.add(svc)
                db.flush()

                if svc_data.unit_values:
                    for uv_data in svc_data.unit_values:
                        uv = QuotationItemServiceUnitValue(
                            quotation_item_service_id=svc.id,
                            unit_id=uv_data.unit_id,
                            value1=uv_data.value1,
                            value2=uv_data.value2,
                        )
                        db.add(uv)

        db.flush()
        db.refresh(item)

        if thickness_option:
            CustomerQuotationRepository._calculate_item_costs(db, item, thickness_option)

        # Update quotation total
        quotation = db.query(Quotation).filter(Quotation.id == data.quotation_id).first()
        if quotation:
            quotation.total = round(sum(i.total for i in quotation.items), 2)

        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def get_quotation_item_by_id(db: Session, item_id: int) -> Optional[QuotationItem]:
        return db.query(QuotationItem).options(
            selectinload(QuotationItem.door_type),
            selectinload(QuotationItem.thickness_option),
            selectinload(QuotationItem.services).selectinload(QuotationItemService.service),
            selectinload(QuotationItem.services).selectinload(QuotationItemService.selected_option),
            selectinload(QuotationItem.services).selectinload(QuotationItemService.unit_values).selectinload(QuotationItemServiceUnitValue.unit),
        ).filter(QuotationItem.id == item_id).first()

    @staticmethod
    def get_quotation_items_by_quotation(db: Session, quotation_id: int) -> List[QuotationItem]:
        return db.query(QuotationItem).options(
            selectinload(QuotationItem.door_type),
            selectinload(QuotationItem.thickness_option),
            selectinload(QuotationItem.services).selectinload(QuotationItemService.service),
            selectinload(QuotationItem.services).selectinload(QuotationItemService.selected_option),
        ).filter(QuotationItem.quotation_id == quotation_id).all()

    @staticmethod
    def update_quotation_item(db: Session, item_id: int, data: QuotationItemUpdate, updated_by: str = None) -> Optional[QuotationItem]:
        item = db.query(QuotationItem).filter(QuotationItem.id == item_id).first()
        if not item:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(item, key, value)
        if updated_by:
            item.updated_by = updated_by
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete_quotation_item(db: Session, item_id: int) -> bool:
        item = db.query(QuotationItem).filter(QuotationItem.id == item_id).first()
        if not item:
            return False
        quotation_id = item.quotation_id
        db.delete(item)
        db.flush()

        # Recalculate quotation total
        quotation = db.query(Quotation).filter(Quotation.id == quotation_id).first()
        if quotation:
            quotation.total = round(sum(i.total for i in quotation.items), 2)

        db.commit()
        return True

    # ========================================================================
    # QUOTATION NUMBER GENERATOR
    # ========================================================================

    @staticmethod
    def generate_quotation_number(db: Session) -> str:
        """Generate next quotation number in Q-YYYY-NNN format."""
        from datetime import date
        year = date.today().year
        prefix = f"Q-{year}-"

        last = db.query(Quotation).filter(
            Quotation.quotation_number.like(f"{prefix}%")
        ).order_by(Quotation.id.desc()).first()

        if last:
            try:
                last_num = int(last.quotation_number.split("-")[-1])
            except (ValueError, IndexError):
                last_num = 0
            next_num = last_num + 1
        else:
            next_num = 1

        return f"{prefix}{next_num:03d}"
