"""
Customer and Quotation Management CRUD Operations
"""

from sqlalchemy.orm import Session, joinedload, selectinload
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, timezone
from time_utils import now_ist
from fastapi import HTTPException, status
from db_helper.models import Customer, Quotation, QuotationItem, QuotationItemAttribute, DoorType, Attribute, UnitValue, DoorTypeThicknessOption, AttributeOption, QuotationItemNestedAttribute, NestedAttribute, CostType
from schemas.schemas import (
    CustomerCreate, CustomerUpdate, CustomerResponse,
    QuotationCreate, QuotationUpdate, QuotationResponse, QuotationShortResponse,
    QuotationItemCreate, QuotationItemUpdate, QuotationItemResponse,
    QuotationItemAttributeCreate, QuotationItemAttributeUpdate, QuotationItemAttributeResponse,
    QuotationItemNestedAttributeCreate, QuotationItemNestedAttributeResponse
)

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
        db.flush()
        return customer

    @staticmethod
    def get_customer_by_id(db: Session, customer_id: int) -> Optional[CustomerResponse]:
        return db.query(Customer).filter(Customer.id == customer_id).first()

    @staticmethod
    def get_all_customers(db: Session, skip: int = 0, limit: int = 100) -> List[CustomerResponse]:
        return db.query(Customer).offset(skip).limit(limit).all()

    @staticmethod
    def count_customers(db: Session) -> int:
        return db.query(Customer).count()

    @staticmethod
    def update_customer(db: Session, customer_id: int, data: CustomerUpdate, username: str = None) -> Optional[CustomerResponse]:
        customer = db.get(Customer, customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(customer, key, value)
        
        customer.updated_by = username
        customer.updated_at = now_ist()

        db.flush()
        return customer

    @staticmethod
    def delete_customer(db: Session, customer_id: int) -> bool:
        customer = db.get(Customer, customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )

        if customer.quotations:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer is associated with quotations"
            )
        
        db.flush()
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
                
                area_sqft = (item.length * item.breadth) / 144
                base_cost_per_unit = area_sqft * thickness_option.cost_per_sqft
                total_base_cost = base_cost_per_unit * item.quantity
                item.quotation_id = quotation.id
                # Create quotation item with initial base costs
                quotation_item = QuotationItem(
                    **item.dict(exclude={"attributes", "nested_attributes"}),
                    created_by=username,
                    updated_by=username,
                    base_cost_per_unit=base_cost_per_unit,
                    attribute_cost_per_unit=0,
                    unit_price_with_attributes=base_cost_per_unit,
                    total_item_cost=total_base_cost
                )
                db.add(quotation_item)
                db.flush()
                attribute_list = []
                item_attribute_costs = []
                per_unit_attribute_total = 0
                if item.nested_attributes:
                    for nested_attribute in item.nested_attributes:
                        quotation_item_nested_attribute = QuotationItemNestedAttribute(
                            nested_attribute_id=nested_attribute.nested_attribute_id,
                            created_by=username,
                            updated_by=username
                        )
                        db.add(quotation_item_nested_attribute)
                        db.flush()
                        for attr in nested_attribute.attributes:
                            attr.quotation_item_nested_attribute_id = quotation_item_nested_attribute.id
                        attribute_list.extend(nested_attribute.attributes)
                if attribute_list:
                    for attr in attribute_list:
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
                        calculated_cost = 0
                        if attribute.cost_type == CostType.DIRECT:
                            calculated_cost = 0
                        else:
                            if selected_option:
                                if attribute.cost_type == CostType.CONSTANT:
                                    calculated_cost = selected_option.cost
                                elif attribute.cost_type == CostType.VARIABLE and attr.unit_values:
                                    if attribute.unit.unit_type == "Linear" and len(attr.unit_values) != 1:
                                        raise ValueError(f"Linear attribute {attribute.name} has {len(attr.unit_values)} unit values")
                                    elif attribute.unit.unit_type == "Vector" and len(attr.unit_values) != 2:
                                        raise ValueError(f"Vector attribute {attribute.name} has {len(attr.unit_values)} unit values")
                                    if attribute.unit.unit_type == "Linear":
                                        calculated_cost = selected_option.cost * attr.unit_values[0].value1
                                    elif attribute.unit.unit_type == "Vector":
                                        calculated_cost = selected_option.cost * attr.unit_values[0].value1 * attr.unit_values[1].value2
                            else:
                                if attribute.cost_type == CostType.CONSTANT:
                                    calculated_cost = attribute.cost
                                elif attribute.cost_type == CostType.VARIABLE and attr.unit_values:
                                    if attribute.unit.unit_type == "Linear" and len(attr.unit_values) != 1:
                                        raise ValueError(f"Linear attribute {attribute.name} has {len(attr.unit_values)} unit values")
                                    elif attribute.unit.unit_type == "Vector" and len(attr.unit_values) != 2:
                                        raise ValueError(f"Vector attribute {attribute.name} has {len(attr.unit_values)} unit values")
                                    if attribute.unit.unit_type == "Linear":
                                        calculated_cost = attribute.cost * attr.unit_values[0].value1
                                    elif attribute.unit.unit_type == "Vector":
                                        calculated_cost = attribute.cost * attr.unit_values[0].value1 * attr.unit_values[1].value2

                        if attribute.cost_type == CostType.DIRECT:
                            total_attribute_cost = attr.direct_cost
                        else:
                            total_attribute_cost = calculated_cost
                        
                        if attr.double_side:
                            total_attribute_cost *= 2

                        # Create quotation item attribute with calculated costs
                        quotation_item_attribute = QuotationItemAttribute(
                            quotation_item_id=quotation_item.id,
                            quotation_item_nested_attribute_id=attr.quotation_item_nested_attribute_id,
                            attribute_id=attr.attribute_id,
                            selected_option_id=attr.selected_option_id,
                            double_side=attr.double_side,
                            direct_cost=attr.direct_cost,
                            calculated_cost=calculated_cost,
                            total_attribute_cost=total_attribute_cost,
                            created_by=username,
                            updated_by=username
                        )
                        db.add(quotation_item_attribute)
                        db.flush()
                        
                        # Store unit values if provided
                        if attr.unit_values:
                            for unit_value in attr.unit_values:
                                unit_value.quotation_item_attribute_id = quotation_item_attribute.id
                                quotation_item_attribute_unit_value = UnitValue(
                                    **unit_value.dict()
                                )
                                db.add(quotation_item_attribute_unit_value)
                                db.flush()
                        
                        # Track costs for this item
                        item_attribute_costs.append(quotation_item_attribute)
                        per_unit_attribute_total += total_attribute_cost
                
                quotation_item.attribute_cost_per_unit = per_unit_attribute_total
                quotation_item.unit_price_with_attributes = quotation_item.base_cost_per_unit + per_unit_attribute_total
                discount_amount = item.discount_amount or 0
                quotation_item.unit_price_with_discount = quotation_item.unit_price_with_attributes - discount_amount
                tax_percentage = item.tax_percentage or 0
                quotation_item.unit_price_with_tax = quotation_item.unit_price_with_discount * (1 + tax_percentage / 100)
                quotation_item.total_item_cost = quotation_item.unit_price_with_tax * item.quantity
                total_quotation_cost += quotation_item.total_item_cost

        quotation.total_amount = total_quotation_cost
        
        db.flush()
        return quotation

    @staticmethod
    def get_quotation_by_id(db: Session, quotation_id: int) -> Optional[QuotationResponse]:
        return db.query(Quotation).options(
            joinedload(Quotation.customer),
            joinedload(Quotation.items).options(
                joinedload(QuotationItem.door_type),
                joinedload(QuotationItem.attributes).joinedload(QuotationItemAttribute.unit_values).selectinload(UnitValue.unit),
                joinedload(QuotationItem.attributes).joinedload(QuotationItemAttribute.quotation_item_nested_attribute),
                joinedload(QuotationItem.attributes).joinedload(QuotationItemAttribute.attribute)
            )
        ).filter(Quotation.id == quotation_id).first()

    @staticmethod
    def get_quotation_by_number(db: Session, quotation_number: str) -> Optional[QuotationResponse]:
        return db.query(Quotation).options(
            joinedload(Quotation.customer),
            joinedload(Quotation.items).options(
                joinedload(QuotationItem.door_type),
                joinedload(QuotationItem.attributes).joinedload(QuotationItemAttribute.unit_values).selectinload(UnitValue.unit),
                joinedload(QuotationItem.attributes).joinedload(QuotationItemAttribute.quotation_item_nested_attribute).joinedload(QuotationItemNestedAttribute.nested_attribute),
                joinedload(QuotationItem.attributes).joinedload(QuotationItemAttribute.attribute)
            )
        ).filter(Quotation.quotation_number == quotation_number).first()

    @staticmethod
    def get_quotations_by_customer(db: Session, customer_id: int) -> List[QuotationResponse]:
        return db.query(Quotation).options(
            joinedload(Quotation.customer),
            joinedload(Quotation.items).options(
                selectinload(QuotationItem.door_type),
                joinedload(QuotationItem.attributes).joinedload(QuotationItemAttribute.unit_values).selectinload(UnitValue.unit),
                joinedload(QuotationItem.attributes).joinedload(QuotationItemAttribute.quotation_item_nested_attribute).selectinload(QuotationItemNestedAttribute.nested_attribute),
                joinedload(QuotationItem.attributes).selectinload(QuotationItemAttribute.attribute)
            )
        ).filter(
            Quotation.customer_id == customer_id
        ).order_by(Quotation.date.desc()).all()


    @staticmethod
    def get_all_quotations(db: Session, skip: int = 0, limit: int = 100) -> List[QuotationShortResponse]:
        return db.query(Quotation).options(
            joinedload(Quotation.customer)
        ).offset(skip).limit(limit).all()

    @staticmethod
    def count_quotations(db: Session) -> int:
        return db.query(Quotation).count()

    @staticmethod
    def recalculate_quotation_costs(db: Session, quotation_id: int) -> Optional[QuotationResponse]:
        quotation = db.query(Quotation).filter(Quotation.id == quotation_id).first()
        if not quotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quotation not found"
            )
        
        total_quotation_cost = 0
        
        # Get all quotation items
        quotation_items = db.query(QuotationItem).filter(
            QuotationItem.quotation_id == quotation_id
        ).all()
        
        for item in quotation_items:
            # Get thickness option for base cost calculation
            thickness_option = db.query(DoorTypeThicknessOption).filter(
                DoorTypeThicknessOption.id == item.thickness_option_id
            ).first()
            
            if not thickness_option:
                continue
            
            # Calculate base cost
            area_sqft = (item.length * item.breadth) / 144
            base_cost_per_unit = area_sqft * thickness_option.cost_per_sqft
            
            # Calculate attribute costs
            per_unit_attribute_total = 0
            
            # Get all attributes for this item
            item_attributes = db.query(QuotationItemAttribute).filter(
                QuotationItemAttribute.quotation_item_id == item.id
            ).all()
            
            for attr in item_attributes:
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
                calculated_cost = 0
                if attribute.cost_type == CostType.DIRECT:
                    calculated_cost =  0
                else:
                    # Get unit values for this attribute
                    unit_values = db.query(UnitValue).filter(
                        UnitValue.quotation_item_attribute_id == attr.id
                    ).all()
                    if selected_option:
                        if attribute.cost_type == CostType.CONSTANT:
                            calculated_cost = selected_option.cost or 0
                        elif attribute.cost_type == CostType.VARIABLE and unit_values:
                            if attribute.unit and attribute.unit.unit_type == "Linear" and len(unit_values) >= 1:
                                calculated_cost = (selected_option.cost or 0) * (unit_values[0].value1 or 0)
                            elif attribute.unit and attribute.unit.unit_type == "Vector" and len(unit_values) >= 2:
                                calculated_cost = (selected_option.cost or 0) * (unit_values[0].value1 or 0) * (unit_values[1].value2 or 0)
                    else:
                        if attribute.cost_type == CostType.CONSTANT:
                            calculated_cost = attribute.cost or 0
                        elif attribute.cost_type == CostType.VARIABLE and unit_values:
                            if attribute.unit and attribute.unit.unit_type == "Linear" and len(unit_values) >= 1:
                                calculated_cost = (attribute.cost or 0) * (unit_values[0].value1 or 0)
                            elif attribute.unit and attribute.unit.unit_type == "Vector" and len(unit_values) >= 2:
                                calculated_cost = (attribute.cost or 0) * (unit_values[0].value1 or 0) * (unit_values[1].value2 or 0)
                    
                # Update the attribute cost
                if attribute.cost_type == CostType.DIRECT:
                    attr.total_attribute_cost = attr.direct_cost
                else:
                    attr.total_attribute_cost = calculated_cost
                    attr.calculated_cost = calculated_cost
                if attr.double_side:
                    attr.total_attribute_cost *= 2
                per_unit_attribute_total += attr.total_attribute_cost
            
            # Update item costs
            item.base_cost_per_unit = base_cost_per_unit
            item.attribute_cost_per_unit = per_unit_attribute_total
            item.unit_price_with_attributes = base_cost_per_unit + per_unit_attribute_total
            
            # Apply discount
            discount_amount = item.discount_amount or 0
            item.unit_price_with_discount = item.unit_price_with_attributes - discount_amount
            
            # Apply tax
            tax_percentage = item.tax_percentage or 0
            item.unit_price_with_tax = item.unit_price_with_discount * (1 + tax_percentage / 100)
            
            # Calculate total item cost
            item.total_item_cost = item.unit_price_with_tax * item.quantity
            total_quotation_cost += item.total_item_cost
        
        # Update quotation total
        quotation.total_amount = total_quotation_cost
        quotation.updated_at = now_ist()
        
        db.flush()
        return quotation

    @staticmethod
    def update_quotation(db: Session, quotation_id: int, data: QuotationUpdate, updated_by: str = None) -> Optional[QuotationResponse]:
        quotation = db.get(Quotation, quotation_id)
        if not quotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quotation not found"
            )

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(quotation, key, value)
        
        quotation.updated_by = updated_by
        quotation.updated_at = now_ist()

        db.flush()
        return quotation

    @staticmethod
    def delete_quotation(db: Session, quotation_id: int) -> bool:
        quotation = db.get(Quotation, quotation_id)
        if not quotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quotation not found"
            )
        
        db.delete(quotation)
        db.flush()
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
        db.flush()
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
            QuotationItem.quotation_id == quotation_id
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
        quotation_item.updated_at = now_ist()

        db.flush()
        return quotation_item

    @staticmethod
    def delete_quotation_item(db: Session, item_id: int) -> bool:
        quotation_item = db.get(QuotationItem, item_id)
        if not quotation_item:
            return False
        db.delete(quotation_item)
        db.flush()
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
        db.flush()
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
            QuotationItemAttribute.quotation_item_id == quotation_item_id
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
        quotation_item_attribute.updated_at = now_ist()

        db.flush()
        return quotation_item_attribute

    @staticmethod
    def delete_quotation_item_attribute(db: Session, attribute_id: int) -> bool:
        quotation_item_attribute = db.get(QuotationItemAttribute, attribute_id)
        if not quotation_item_attribute:
            return False
        
        db.delete(quotation_item_attribute)
        db.flush()
        return True

    # ============================================================================
    # QUOTATION ITEM NESTED ATTRIBUTE METHODS
    # ============================================================================
    
    @staticmethod
    def create_quotation_item_nested_attribute(db: Session, data: QuotationItemNestedAttributeCreate, created_by: str = None) -> QuotationItemNestedAttributeResponse:
        quotation_item_nested_attribute = QuotationItemNestedAttribute(
            quotation_item_id=data.quotation_item_id,
            nested_attribute_id=data.nested_attribute_id,
            created_by=created_by,
            updated_by=created_by
        )
        db.add(quotation_item_nested_attribute)
        db.flush()
        return quotation_item_nested_attribute

    @staticmethod
    def get_quotation_item_nested_attribute_by_id(db: Session, nested_attribute_id: int) -> Optional[QuotationItemNestedAttributeResponse]:
        return db.query(QuotationItemNestedAttribute).options(
            joinedload(QuotationItemNestedAttribute.nested_attribute)
        ).filter(QuotationItemNestedAttribute.id == nested_attribute_id).first()

    @staticmethod
    def get_quotation_item_nested_attributes_by_item(db: Session, quotation_item_id: int) -> List[QuotationItemNestedAttributeResponse]:
        return db.query(QuotationItemNestedAttribute).options(
            joinedload(QuotationItemNestedAttribute.nested_attribute)
        ).filter(
            QuotationItemNestedAttribute.quotation_item_id == quotation_item_id
        ).all()

    @staticmethod
    def update_quotation_item_nested_attribute(db: Session, nested_attribute_id: int, data: dict, updated_by: str = None) -> Optional[QuotationItemNestedAttributeResponse]:
        quotation_item_nested_attribute = db.get(QuotationItemNestedAttribute, nested_attribute_id)
        if not quotation_item_nested_attribute:
            return None

        for key, value in data.items():
            if hasattr(quotation_item_nested_attribute, key):
                setattr(quotation_item_nested_attribute, key, value)
        
        quotation_item_nested_attribute.updated_by = updated_by
        quotation_item_nested_attribute.updated_at = now_ist()

        db.flush()
        return quotation_item_nested_attribute

    @staticmethod
    def delete_quotation_item_nested_attribute(db: Session, nested_attribute_id: int) -> bool:
        quotation_item_nested_attribute = db.get(QuotationItemNestedAttribute, nested_attribute_id)
        if not quotation_item_nested_attribute:
            return False
        
        db.delete(quotation_item_nested_attribute)
        db.flush()
        return True

    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    @staticmethod
    def generate_quotation_number(db: Session) -> str:
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
