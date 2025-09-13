"""
Customer and Quotation Management CRUD Operations
"""

from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from db_helper.models import Customer, Quotation, QuotationItem, QuotationItemAttribute, DoorType, Attribute, UnitValue, DoorTypeThicknessOption, AttributeOption
from schemas.schemas import (
    CustomerCreate, CustomerUpdate, CustomerResponse,
    QuotationCreate, QuotationUpdate, QuotationResponse,
    QuotationItemCreate, QuotationItemUpdate, QuotationItemResponse,
    QuotationItemAttributeCreate, QuotationItemAttributeUpdate, QuotationItemAttributeResponse,
)
from db_helper.cost_calculations import CostCalculator

# Import for comprehensive quotation creation
from typing import List as TypeList


class CustomerQuotationCRUD:
    # ============================================================================
    # CUSTOMER METHODS
    # ============================================================================
    
    @staticmethod
    def create_customer(db: Session, data: CustomerCreate, username: str = None) -> CustomerResponse:
        customer = Customer(
            **data.dict(),
            created_by=username,
            updated_by=username
        )
        db.add(customer)
        db.commit()
        return customer

    @staticmethod
    def get_customer_by_id(db: Session, customer_id: int) -> Optional[CustomerResponse]:
        return db.query(Customer).filter(Customer.id == customer_id).first()

    @staticmethod
    def get_all_customers(db: Session, skip: int = 0, limit: int = 100) -> List[CustomerResponse]:
        return db.query(Customer).offset(skip).limit(limit).all()

    @staticmethod
    def get_active_customers(db: Session) -> List[CustomerResponse]:
        return db.query(Customer).filter(Customer.is_active == True).all()

    @staticmethod
    def update_customer(db: Session, customer_id: int, data: CustomerUpdate, username: str = None) -> Optional[CustomerResponse]:
        customer = db.get(Customer, customer_id)
        if not customer:
            return None

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(customer, key, value)
        
        customer.updated_by = username
        customer.updated_at = datetime.now(timezone.utc)

        db.commit()
        return customer

    @staticmethod
    def delete_customer(db: Session, customer_id: int) -> bool:
        customer = db.get(Customer, customer_id)
        if not customer:
            return False
        
        # Soft delete - just mark as inactive
        customer.is_active = False
        db.commit()
        return True

    # ============================================================================
    # QUOTATION METHODS
    # ============================================================================
    
    @staticmethod
    def create_quotation(db: Session, data: QuotationCreate, username: str = None) -> QuotationResponse:
        """
        Create a quotation with comprehensive cost calculations
        """
        quotation_number = CustomerQuotationCRUD.generate_quotation_number(db)
        quotation = Quotation(
            **data.dict(exclude="items"),
            quotation_number=quotation_number,
            created_by=username,
            updated_by=username
        )
        db.add(quotation)
        db.flush()
        
        total_quotation_cost = 0
        
        if data.items:
            for item in data.items:
                # Get thickness option for cost calculation
                thickness_option = db.query(DoorTypeThicknessOption).filter(
                    DoorTypeThicknessOption.id == item.thickness_option_id
                ).first()
                
                if not thickness_option:
                    raise ValueError(f"Thickness option {item.thickness_option_id} not found")
                
                # Calculate base cost per unit (for one door)
                base_cost_breakdown = CostCalculator.calculate_base_cost(
                    length=item.length,
                    breadth=item.breadth,
                    thickness_option=thickness_option,
                    quantity=1
                )
                item.quotation_id = quotation.id
                # Create quotation item with initial base costs
                quotation_item = QuotationItem(
                    **item.dict(exclude="attributes"),
                    created_by=username,
                    updated_by=username,
                    base_cost_per_unit=base_cost_breakdown['base_cost_per_unit'],
                    attribute_cost_per_unit=0,
                    unit_price_with_attributes=base_cost_breakdown['base_cost_per_unit'],
                    total_item_cost=base_cost_breakdown['total_base_cost']
                )
                db.add(quotation_item)
                db.flush()
                
                item_attribute_costs = []
                per_unit_attribute_total = 0
                
                if item.attributes:
                    for attr in item.attributes:
                        # Get the attribute details
                        attribute = db.query(Attribute).filter(Attribute.id == attr.attribute_id).first()
                        if not attribute:
                            continue
                        
                        # Get selected option if applicable
                        selected_option = None
                        if attr.selected_option_id:
                            selected_option = db.query(AttributeOption).filter(
                                AttributeOption.id == attr.selected_option_id
                            ).first()
                        
                        # Calculate attribute cost
                        attr_cost_breakdown = CostCalculator.calculate_attribute_cost(
                            db=db,
                            attribute=attribute,
                            selected_option=selected_option,
                            unit_values=attr.unit_values if hasattr(attr, 'unit_values') else None,
                            double_side=attr.double_side,
                            direct_cost=attr.direct_cost if hasattr(attr, 'direct_cost') else None,
                            child_options={}
                        )
                        
                        # Create quotation item attribute with calculated costs
                        quotation_item_attribute = QuotationItemAttribute(
                            quotation_item_id=quotation_item.id,
                            attribute_id=attr.attribute_id,
                            selected_option_id=attr.selected_option_id,
                            double_side=attr.double_side,
                            direct_cost=attr_cost_breakdown['direct_cost'],
                            calculated_cost=attr_cost_breakdown['calculated_cost'],
                            total_attribute_cost=attr_cost_breakdown['total_cost'],
                            created_by=username,
                            updated_by=username
                        )
                        db.add(quotation_item_attribute)
                        db.flush()
                        
                        # Store unit values if provided
                        if hasattr(attr, 'unit_values') and attr.unit_values:
                            for unit_value in attr.unit_values:
                                unit_value.quotation_item_attribute_id = quotation_item_attribute.id
                                quotation_item_attribute_unit_value = UnitValue(
                                    **unit_value.dict()
                                )
                                db.add(quotation_item_attribute_unit_value)
                                db.flush()
                        
                        # Track costs for this item
                        item_attribute_costs.append(attr_cost_breakdown)
                        per_unit_attribute_total += attr_cost_breakdown['total_cost']
                
                # Compute per-unit with attributes and total for quantity
                unit_price_with_attributes = base_cost_breakdown['base_cost_per_unit'] + per_unit_attribute_total
                total_item_cost = unit_price_with_attributes * (item.quantity or 1)

                # Update item with calculated costs
                quotation_item.base_cost_per_unit = base_cost_breakdown['base_cost_per_unit']
                quotation_item.attribute_cost_per_unit = per_unit_attribute_total
                quotation_item.unit_price_with_attributes = unit_price_with_attributes
                quotation_item.total_item_cost = total_item_cost
                total_quotation_cost += total_item_cost
        
        # Update quotation total
        quotation.total_amount = total_quotation_cost
        
        db.commit()
        return quotation

    @staticmethod
    def get_quotation_by_id(db: Session, quotation_id: int) -> Optional[QuotationResponse]:
        return db.query(Quotation).options(
            joinedload(Quotation.customer),
            joinedload(Quotation.items).joinedload(QuotationItem.door_type),
            joinedload(Quotation.items).joinedload(QuotationItem.attributes).joinedload(QuotationItemAttribute.attribute)
        ).filter(Quotation.id == quotation_id).first()

    @staticmethod
    def get_quotation_by_number(db: Session, quotation_number: str) -> Optional[QuotationResponse]:
        return db.query(Quotation).options(
            joinedload(Quotation.customer),
            joinedload(Quotation.items).joinedload(QuotationItem.door_type),
            joinedload(Quotation.items).joinedload(QuotationItem.attributes).joinedload(QuotationItemAttribute.attribute)
        ).filter(Quotation.quotation_number == quotation_number).first()

    @staticmethod
    def get_quotations_by_customer(db: Session, customer_id: int) -> List[QuotationResponse]:
        return db.query(Quotation).options(
            joinedload(Quotation.customer),
            joinedload(Quotation.items).joinedload(QuotationItem.door_type),
            joinedload(Quotation.items).joinedload(QuotationItem.attributes).joinedload(QuotationItemAttribute.attribute)
        ).filter(
            Quotation.customer_id == customer_id
        ).order_by(Quotation.date.desc()).all()

    @staticmethod
    def get_all_quotations(db: Session, skip: int = 0, limit: int = 100) -> List[QuotationResponse]:
        return db.query(Quotation).options(
            joinedload(Quotation.customer),
            joinedload(Quotation.items).joinedload(QuotationItem.door_type),
            joinedload(Quotation.items).joinedload(QuotationItem.attributes).joinedload(QuotationItemAttribute.attribute)
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_quotations_by_status(db: Session, status: str) -> List[QuotationResponse]:
        return db.query(Quotation).options(
            joinedload(Quotation.customer),
            joinedload(Quotation.items).joinedload(QuotationItem.door_type),
            joinedload(Quotation.items).joinedload(QuotationItem.attributes).joinedload(QuotationItemAttribute.attribute)
        ).filter(
            Quotation.status == status
        ).order_by(Quotation.date.desc()).all()

    @staticmethod
    def update_quotation(db: Session, quotation_id: int, data: QuotationUpdate, updated_by: str = None) -> Optional[QuotationResponse]:
        quotation = db.get(Quotation, quotation_id)
        if not quotation:
            return None

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(quotation, key, value)
        
        quotation.updated_by = updated_by
        quotation.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(quotation)
        return quotation

    @staticmethod
    def delete_quotation(db: Session, quotation_id: int) -> bool:
        quotation = db.get(Quotation, quotation_id)
        if not quotation:
            return False
        
        # Soft delete - just mark as inactive
        # quotation.is_active = False
        db.delete(quotation)
        db.commit()
        return True

    # ============================================================================
    # QUOTATION ITEM METHODS
    # ============================================================================
    
    @staticmethod
    def create_quotation_item(db: Session, data: QuotationItemCreate, created_by: str = None) -> QuotationItemResponse:
        quotation_item = QuotationItem(
            quotation_id=data.quotation_id,
            door_type_id=data.door_type_id,
            thickness_option_id=data.thickness_option_id,
            length=data.length,
            breadth=data.breadth,
            quantity=data.quantity,
            created_by=created_by
        )
        db.add(quotation_item)
        db.commit()
        db.refresh(quotation_item)
        return quotation_item

    @staticmethod
    def get_quotation_item_by_id(db: Session, item_id: int) -> Optional[QuotationItemResponse]:
        return db.query(QuotationItem).options(
            joinedload(QuotationItem.door_type),
            joinedload(QuotationItem.attributes).joinedload(QuotationItemAttribute.attribute)
        ).filter(QuotationItem.id == item_id).first()

    @staticmethod
    def get_quotation_items_by_quotation(db: Session, quotation_id: int) -> List[QuotationItemResponse]:
        return db.query(QuotationItem).options(
            joinedload(QuotationItem.door_type),
            joinedload(QuotationItem.attributes).joinedload(QuotationItemAttribute.attribute)
        ).filter(
            QuotationItem.quotation_id == quotation_id,
            QuotationItem.is_active == True
        ).all()

    @staticmethod
    def update_quotation_item(db: Session, item_id: int, data: QuotationItemUpdate, updated_by: str = None) -> Optional[QuotationItemResponse]:
        quotation_item = db.get(QuotationItem, item_id)
        if not quotation_item:
            return None

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(quotation_item, key, value)
        
        quotation_item.updated_by = updated_by
        quotation_item.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(quotation_item)
        return quotation_item

    @staticmethod
    def delete_quotation_item(db: Session, item_id: int) -> bool:
        quotation_item = db.get(QuotationItem, item_id)
        if not quotation_item:
            return False
        
        # Soft delete - just mark as inactive
        quotation_item.is_active = False
        db.commit()
        return True

    # ============================================================================
    # QUOTATION ITEM ATTRIBUTE METHODS
    # ============================================================================
    
    @staticmethod
    def create_quotation_item_attribute(db: Session, data: QuotationItemAttributeCreate, created_by: str = None) -> QuotationItemAttributeResponse:
        quotation_item_attribute = QuotationItemAttribute(
            quotation_item_id=data.quotation_item_id,
            attribute_id=data.attribute_id,
            selected_option_id=data.selected_option_id,
            double_side=data.double_side,
            direct_cost=data.direct_cost,
            created_by=created_by
        )
        db.add(quotation_item_attribute)
        db.commit()
        db.refresh(quotation_item_attribute)
        return quotation_item_attribute

    @staticmethod
    def get_quotation_item_attribute_by_id(db: Session, attribute_id: int) -> Optional[QuotationItemAttributeResponse]:
        return db.query(QuotationItemAttribute).options(
            joinedload(QuotationItemAttribute.attribute)
        ).filter(QuotationItemAttribute.id == attribute_id).first()

    @staticmethod
    def get_quotation_item_attributes_by_item(db: Session, quotation_item_id: int) -> List[QuotationItemAttributeResponse]:
        return db.query(QuotationItemAttribute).options(
            joinedload(QuotationItemAttribute.attribute)
        ).filter(
            QuotationItemAttribute.quotation_item_id == quotation_item_id,
            QuotationItemAttribute.is_active == True
        ).all()

    @staticmethod
    def update_quotation_item_attribute(db: Session, attribute_id: int, data: QuotationItemAttributeUpdate, updated_by: str = None) -> Optional[QuotationItemAttributeResponse]:
        quotation_item_attribute = db.get(QuotationItemAttribute, attribute_id)
        if not quotation_item_attribute:
            return None

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(quotation_item_attribute, key, value)
        
        quotation_item_attribute.updated_by = updated_by
        quotation_item_attribute.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(quotation_item_attribute)
        return quotation_item_attribute

    @staticmethod
    def delete_quotation_item_attribute(db: Session, attribute_id: int) -> bool:
        quotation_item_attribute = db.get(QuotationItemAttribute, attribute_id)
        if not quotation_item_attribute:
            return False
        
        # Soft delete - just mark as inactive
        quotation_item_attribute.is_active = False
        db.commit()
        return True

    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    @staticmethod
    def generate_quotation_number(db: Session) -> str:
        """Generate a unique quotation number"""
        # Get current year and month
        now = datetime.now()
        year_month = now.strftime("%Y%m")
        
        # Get the last quotation number for this month
        last_quotation = db.query(Quotation).filter(
            Quotation.quotation_number.like(f"QT{year_month}%")
        ).order_by(Quotation.quotation_number.desc()).first()
        
        if last_quotation:
            # Extract the sequence number and increment
            try:
                last_seq = int(last_quotation.quotation_number[-4:])
                new_seq = last_seq + 1
            except ValueError:
                new_seq = 1
        else:
            new_seq = 1
        
        # Format: QT2024010001
        return f"QT{year_month}{new_seq:04d}"

    @staticmethod
    def get_quotation_summary(db: Session, quotation_id: int) -> Dict[str, Any]:
        """Get a summary of quotation details including totals"""
        quotation = db.get(Quotation, quotation_id)
        if not quotation:
            return {}
        
        items = db.query(QuotationItem).filter(
            QuotationItem.quotation_id == quotation_id,
            QuotationItem.is_active == True
        ).all()
        
        total_items = len(items)
        total_quantity = sum(item.quantity or 0 for item in items)
        total_amount = sum(float(item.total_item_cost or 0) for item in items)
        
        return {
            "quotation_id": quotation.id,
            "quotation_number": getattr(quotation, 'quotation_number', None),
            "customer_name": quotation.customer.name if quotation.customer else None,
            "total_items": total_items,
            "total_quantity": total_quantity,
            "total_amount": total_amount,
            "status": quotation.status,
            "date": quotation.date,
            "valid_until": getattr(quotation, 'valid_until', None)
        }

    @staticmethod
    def get_quotation_cost_breakdown(db: Session, quotation_id: int) -> Dict[str, Any]:
        """
        Get detailed cost breakdown for a quotation including all calculations
        """
        return CostCalculator.get_quotation_cost_breakdown(db, quotation_id)

    @staticmethod
    def recalculate_quotation_costs(db: Session, quotation_id: int, username: str = None) -> Dict[str, Any]:
        """
        Recalculate all costs for an existing quotation
        Useful when attribute costs or thickness options change
        """
        return CostCalculator.recalculate_quotation_costs(db, quotation_id, username)
