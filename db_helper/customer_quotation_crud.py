"""
Customer and Quotation Management CRUD Operations
"""

from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from db_helper.models import Customer, Quotation, QuotationItem, QuotationItemAttribute, DoorType, Attribute
from schemas.schemas import (
    CustomerCreate, CustomerUpdate, CustomerResponse,
    QuotationCreate, QuotationUpdate, QuotationResponse,
    QuotationItemCreate, QuotationItemUpdate, QuotationItemResponse,
    QuotationItemAttributeCreate, QuotationItemAttributeUpdate, QuotationItemAttributeResponse,
    ComprehensiveQuotationCreate
)

# Import for comprehensive quotation creation
from typing import List as TypeList


class CustomerQuotationCRUD:
    # ============================================================================
    # CUSTOMER METHODS
    # ============================================================================
    
    @staticmethod
    def create_customer(db: Session, data: CustomerCreate, created_by: str = None) -> CustomerResponse:
        customer = Customer(
            name=data.name,
            email=data.email,
            phone=data.phone,
            address=data.address,
            city=data.city,
            state=data.state,
            postal_code=data.postal_code,
            country=data.country,
            is_active=data.is_active,
            created_by=created_by
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer

    @staticmethod
    def get_customer_by_id(db: Session, customer_id: int) -> Optional[Customer]:
        return db.query(Customer).filter(Customer.id == customer_id).first()

    @staticmethod
    def get_customer_by_email(db: Session, email: str) -> Optional[Customer]:
        return db.query(Customer).filter(Customer.email == email).first()

    @staticmethod
    def get_customer_by_phone(db: Session, phone: str) -> Optional[Customer]:
        return db.query(Customer).filter(Customer.phone == phone).first()

    @staticmethod
    def get_all_customers(db: Session, skip: int = 0, limit: int = 100) -> List[Customer]:
        return db.query(Customer).offset(skip).limit(limit).all()

    @staticmethod
    def get_active_customers(db: Session) -> List[Customer]:
        return db.query(Customer).filter(Customer.is_active == True).all()

    @staticmethod
    def search_customers(db: Session, search_term: str) -> List[Customer]:
        """Search customers by name, email, or phone"""
        return db.query(Customer).filter(
            Customer.is_active == True,
            (Customer.name.ilike(f"%{search_term}%") |
             Customer.email.ilike(f"%{search_term}%") |
             Customer.phone.ilike(f"%{search_term}%"))
        ).all()

    @staticmethod
    def update_customer(db: Session, customer_id: int, data: CustomerUpdate, updated_by: str = None) -> Optional[Customer]:
        customer = db.get(Customer, customer_id)
        if not customer:
            return None

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(customer, key, value)
        
        customer.updated_by = updated_by
        customer.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(customer)
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
    def create_quotation(db: Session, data: QuotationCreate, created_by: str = None) -> QuotationResponse:
        quotation = Quotation(
            customer_id=data.customer_id,
            quotation_number=data.quotation_number,
            quotation_date=data.quotation_date,
            valid_until=data.valid_until,
            total_amount=data.total_amount,
            status=data.status,
            notes=data.notes,
            created_by_employee_id=data.created_by_employee_id,
            updated_by_employee_id=data.updated_by_employee_id,
            is_active=data.is_active,
            created_by=created_by
        )
        db.add(quotation)
        db.commit()
        db.refresh(quotation)
        return quotation

    @staticmethod
    def get_quotation_by_id(db: Session, quotation_id: int) -> Optional[Quotation]:
        return db.query(Quotation).options(
            joinedload(Quotation.customer),
            joinedload(Quotation.items).joinedload(QuotationItem.door_type),
            joinedload(Quotation.items).joinedload(QuotationItem.attributes).joinedload(QuotationItemAttribute.attribute),
            joinedload(Quotation.created_by_employee),
            joinedload(Quotation.updated_by_employee)
        ).filter(Quotation.id == quotation_id).first()

    @staticmethod
    def get_quotation_by_number(db: Session, quotation_number: str) -> Optional[Quotation]:
        return db.query(Quotation).options(
            joinedload(Quotation.customer),
            joinedload(Quotation.items).joinedload(QuotationItem.door_type),
            joinedload(Quotation.items).joinedload(QuotationItem.attributes).joinedload(QuotationItemAttribute.attribute)
        ).filter(Quotation.quotation_number == quotation_number).first()

    @staticmethod
    def get_quotations_by_customer(db: Session, customer_id: int) -> List[Quotation]:
        return db.query(Quotation).options(
            joinedload(Quotation.customer),
            joinedload(Quotation.items).joinedload(QuotationItem.door_type),
            joinedload(Quotation.items).joinedload(QuotationItem.attributes).joinedload(QuotationItemAttribute.attribute)
        ).filter(
            Quotation.customer_id == customer_id,
            Quotation.is_active == True
        ).order_by(Quotation.quotation_date.desc()).all()

    @staticmethod
    def get_all_quotations(db: Session, skip: int = 0, limit: int = 100) -> List[Quotation]:
        return db.query(Quotation).options(
            joinedload(Quotation.customer),
            joinedload(Quotation.items).joinedload(QuotationItem.door_type),
            joinedload(Quotation.items).joinedload(QuotationItem.attributes).joinedload(QuotationItemAttribute.attribute)
        ).offset(skip).limit(limit).order_by(Quotation.quotation_date.desc()).all()

    @staticmethod
    def get_quotations_by_status(db: Session, status: str) -> List[Quotation]:
        return db.query(Quotation).options(
            joinedload(Quotation.customer),
            joinedload(Quotation.items).joinedload(QuotationItem.door_type),
            joinedload(Quotation.items).joinedload(QuotationItem.attributes).joinedload(QuotationItemAttribute.attribute)
        ).filter(
            Quotation.status == status,
            Quotation.is_active == True
        ).order_by(Quotation.quotation_date.desc()).all()

    @staticmethod
    def update_quotation(db: Session, quotation_id: int, data: QuotationUpdate, updated_by: str = None) -> Optional[Quotation]:
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
        quotation.is_active = False
        db.commit()
        return True

    @staticmethod
    def calculate_quotation_total(db: Session, quotation_id: int) -> float:
        """Calculate total amount for a quotation based on its items"""
        quotation = db.get(Quotation, quotation_id)
        if not quotation:
            return 0.0
        
        total = 0.0
        for item in quotation.items:
            if item.is_active:
                total += item.total_price or 0.0
        
        return total

    @staticmethod
    def create_comprehensive_quotation(
        db: Session, 
        quotation_data: ComprehensiveQuotationCreate, 
        created_by: str = None
    ) -> QuotationResponse:
        """
        Create a complete quotation with items and attributes in one transaction.
        Uses proper Pydantic schemas for type safety and validation.
        """
        try:
            # Start transaction
            db.begin()
            
            # Generate quotation number if not provided
            if not quotation_data.quotation_number:
                quotation_data.quotation_number = CustomerQuotationCRUD.generate_quotation_number(db)
            
            # Create quotation
            quotation = Quotation(
                customer_id=quotation_data.customer_id,
                quotation_number=quotation_data.quotation_number,
                quotation_date=quotation_data.quotation_date,
                valid_until=quotation_data.valid_until,
                status=quotation_data.status,
                notes=quotation_data.notes,
                created_by_employee_id=quotation_data.created_by_employee_id,
                updated_by_employee_id=quotation_data.updated_by_employee_id,
                is_active=True,
                created_by=created_by
            )
            
            db.add(quotation)
            db.flush()  # Get the quotation ID
            
            total_quotation_amount = 0.0
            
            # Process each item
            for item_data in quotation_data.items:
                # Calculate base item price
                door_type = db.get(DoorType, item_data.door_type_id)
                if not door_type:
                    raise ValueError(f"Door type {item_data.door_type_id} not found")
                
                base_price = door_type.base_price or 0.0
                quantity = item_data.quantity
                
                # Calculate item total price
                item_total_price = base_price * quantity
                
                # Create quotation item
                quotation_item = QuotationItem(
                    quotation_id=quotation.id,
                    door_type_id=item_data.door_type_id,
                    quantity=quantity,
                    unit_price=base_price,
                    total_price=item_total_price,
                    width=item_data.width,
                    height=item_data.height,
                    thickness=item_data.thickness,
                    notes=item_data.notes,
                    is_active=True,
                    created_by=created_by
                )
                
                db.add(quotation_item)
                db.flush()  # Get the item ID
                
                # Process item attributes and calculate additional costs
                attribute_costs = 0.0
                
                for attr_data in item_data.attributes:
                    attribute = db.get(Attribute, attr_data.attribute_id)
                    if not attribute:
                        raise ValueError(f"Attribute {attr_data.attribute_id} not found")
                    
                    # Calculate attribute cost based on cost type
                    if attribute.cost_type == "constant":
                        attr_cost = attribute.fixed_cost or 0.0
                    elif attribute.cost_type == "variable":
                        attr_cost = (attribute.cost_per_unit or 0.0) * quantity
                    elif attribute.cost_type == "direct":
                        attr_cost = attr_data.cost_adjustment or 0.0
                    else:  # nested
                        attr_cost = 0.0  # Will be calculated separately
                    
                    # Apply double_side logic - if attribute is double-sided, multiply cost by 2
                    if attribute.double_side:
                        attr_cost *= 2
                    
                    # Add custom cost adjustment if provided
                    if attr_data.cost_adjustment:
                        attr_cost += attr_data.cost_adjustment
                    
                    attribute_costs += attr_cost
                    
                    # Create quotation item attribute
                    quotation_item_attribute = QuotationItemAttribute(
                        quotation_item_id=quotation_item.id,
                        attribute_id=attr_data.attribute_id,
                        value=attr_data.value,
                        cost_adjustment=attr_data.cost_adjustment,
                        is_active=True,
                        created_by=created_by
                        )
                    
                    db.add(quotation_item_attribute)
                
                # Update item total price with attribute costs
                item_total_price += attribute_costs
                quotation_item.total_price = item_total_price
                
                # Add to quotation total
                total_quotation_amount += item_total_price
            
            # Update quotation total amount
            quotation.total_amount = total_quotation_amount
            
            # Commit the entire transaction
            db.commit()
            
            # Refresh and return the complete quotation
            db.refresh(quotation)
            
            # Return the quotation with all relationships loaded
            return CustomerQuotationCRUD.get_quotation_by_id(db, quotation.id)
            
        except Exception as e:
            # Rollback on any error
            db.rollback()
            raise e

    @staticmethod
    def calculate_item_total_with_attributes(db: Session, item_id: int) -> float:
        """Calculate total price for a quotation item including all attributes"""
        item = db.get(QuotationItem, item_id)
        if not item:
            return 0.0
        
        # Base price
        base_price = item.unit_price or 0.0
        quantity = item.quantity or 1
        total = base_price * quantity
        
        # Add attribute costs
        for attr in item.attributes:
            if attr.is_active and attr.attribute:
                attr_cost = 0.0
                
                if attr.attribute.cost_type == "constant":
                    attr_cost = attr.attribute.fixed_cost or 0.0
                elif attr.attribute.cost_type == "variable":
                    attr_cost = (attr.attribute.cost_per_unit or 0.0) * quantity
                elif attr.attribute.cost_type == "direct":
                    attr_cost = attr.cost_adjustment or 0.0
                # Note: nested attributes are handled separately
                
                # Apply double_side logic - if attribute is double-sided, multiply cost by 2
                if attr.attribute.double_side:
                    attr_cost *= 2
                
                total += attr_cost
        
        return total

    # ============================================================================
    # QUOTATION ITEM METHODS
    # ============================================================================
    
    @staticmethod
    def create_quotation_item(db: Session, data: QuotationItemCreate, created_by: str = None) -> QuotationItemResponse:
        quotation_item = QuotationItem(
            quotation_id=data.quotation_id,
            door_type_id=data.door_type_id,
            quantity=data.quantity,
            unit_price=data.unit_price,
            total_price=data.total_price,
            width=data.width,
            height=data.height,
            thickness=data.thickness,
            notes=data.notes,
            is_active=data.is_active,
            created_by=created_by
        )
        db.add(quotation_item)
        db.commit()
        db.refresh(quotation_item)
        return quotation_item

    @staticmethod
    def get_quotation_item_by_id(db: Session, item_id: int) -> Optional[QuotationItem]:
        return db.query(QuotationItem).options(
            joinedload(QuotationItem.door_type),
            joinedload(QuotationItem.attributes).joinedload(QuotationItemAttribute.attribute)
        ).filter(QuotationItem.id == item_id).first()

    @staticmethod
    def get_quotation_items_by_quotation(db: Session, quotation_id: int) -> List[QuotationItem]:
        return db.query(QuotationItem).options(
            joinedload(QuotationItem.door_type),
            joinedload(QuotationItem.attributes).joinedload(QuotationItemAttribute.attribute)
        ).filter(
            QuotationItem.quotation_id == quotation_id,
            QuotationItem.is_active == True
        ).all()

    @staticmethod
    def update_quotation_item(db: Session, item_id: int, data: QuotationItemUpdate, updated_by: str = None) -> Optional[QuotationItem]:
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

    @staticmethod
    def calculate_item_total(db: Session, item_id: int) -> float:
        """Calculate total price for a quotation item"""
        item = db.get(QuotationItem, item_id)
        if not item:
            return 0.0
        
        base_price = item.unit_price or 0.0
        quantity = item.quantity or 1
        
        # Calculate base total
        total = base_price * quantity
        
        # Add attribute costs
        for attr in item.attributes:
            if attr.is_active:
                if attr.attribute.cost_type == 'constant':
                    total += attr.attribute.fixed_cost or 0.0
                elif attr.attribute.cost_type == 'variable':
                    total += (attr.attribute.cost_per_unit or 0.0) * quantity
        
        return total

    # ============================================================================
    # QUOTATION ITEM ATTRIBUTE METHODS
    # ============================================================================
    
    @staticmethod
    def create_quotation_item_attribute(db: Session, data: QuotationItemAttributeCreate, created_by: str = None) -> QuotationItemAttributeResponse:
        quotation_item_attribute = QuotationItemAttribute(
            quotation_item_id=data.quotation_item_id,
            attribute_id=data.attribute_id,
            value=data.value,
            cost_adjustment=data.cost_adjustment,
            is_active=data.is_active,
            created_by=created_by
        )
        db.add(quotation_item_attribute)
        db.commit()
        db.refresh(quotation_item_attribute)
        return quotation_item_attribute

    @staticmethod
    def get_quotation_item_attribute_by_id(db: Session, attribute_id: int) -> Optional[QuotationItemAttribute]:
        return db.query(QuotationItemAttribute).options(
            joinedload(QuotationItemAttribute.attribute)
        ).filter(QuotationItemAttribute.id == attribute_id).first()

    @staticmethod
    def get_quotation_item_attributes_by_item(db: Session, quotation_item_id: int) -> List[QuotationItemAttribute]:
        return db.query(QuotationItemAttribute).options(
            joinedload(QuotationItemAttribute.attribute)
        ).filter(
            QuotationItemAttribute.quotation_item_id == quotation_item_id,
            QuotationItemAttribute.is_active == True
        ).all()

    @staticmethod
    def update_quotation_item_attribute(db: Session, attribute_id: int, data: QuotationItemAttributeUpdate, updated_by: str = None) -> Optional[QuotationItemAttribute]:
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
        from datetime import datetime
        
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
        total_amount = sum(item.total_price or 0 for item in items)
        
        return {
            "quotation_id": quotation.id,
            "quotation_number": quotation.quotation_number,
            "customer_name": quotation.customer.name if quotation.customer else None,
            "total_items": total_items,
            "total_quantity": total_quantity,
            "total_amount": total_amount,
            "status": quotation.status,
            "quotation_date": quotation.quotation_date,
            "valid_until": quotation.valid_until
        }
