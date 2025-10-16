"""
Ezzy Traders Database Models
Organized by functional groups for better maintainability and understanding.

Functional Groups:
1. Employee Management
2. Door and Attribute Management
3. Customer and Quotation Management
4. Unit and Measurement Management
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, PrimaryKeyConstraint, func, \
    Enum as SAEnum, Date, Boolean, UniqueConstraint, and_, Float
from sqlalchemy.orm import relationship, foreign
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum as PyEnum
from datetime import date
from time_utils import now_ist

# SQLAlchemy Base declaration
Base = declarative_base()


# ============================================================================
# 1. EMPLOYEE MANAGEMENT GROUP
# ============================================================================

class Employee(Base):
    __tablename__ = "employee"

    id = Column(Integer, primary_key=True, index=True)
    
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    role = Column(String, nullable=False, default="viewer")  # Simple string role

    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)


# ============================================================================
# 2. Customer MANAGEMENT GROUP
# ============================================================================

class Customer(Base):
    __tablename__ = 'customer_details'
    
    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    postal_code = Column(String)
    country = Column(String)
    
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    quotations = relationship('Quotation', back_populates='customer')


# ============================================================================
# 3. DOOR AND ATTRIBUTE MANAGEMENT GROUP
# ============================================================================

class CostType(PyEnum):
    CONSTANT = 'constant'
    VARIABLE = 'variable'
    DIRECT = 'direct'


class DoorType(Base):
    __tablename__ = 'door_type'
    
    id = Column(Integer, primary_key=True)
    
    name = Column(String, nullable=False)
    description = Column(String)
    
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    # Many-to-many with Attribute via DoorTypeAttribute
    door_type_attributes = relationship('DoorTypeAttribute', back_populates='door_type', cascade="all, delete-orphan")
    # One-to-many to quotation items
    items = relationship('QuotationItem', back_populates='door_type')
    # One-to-many to thickness options
    thickness_options = relationship('DoorTypeThicknessOption', back_populates='door_type')


class DoorTypeThicknessOption(Base):
    __tablename__ = 'door_type_thickness_option'
    
    id = Column(Integer, primary_key=True)
    door_type_id = Column(Integer, ForeignKey('door_type.id'), nullable=False)
    
    thickness_value = Column(Float, nullable=False)  # Thickness in mm
    cost_per_sqft = Column(Float, nullable=False)  # Cost per square foot for this thickness
    
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    door_type = relationship('DoorType', back_populates='thickness_options')
    quotation_items = relationship('QuotationItem', back_populates='thickness_option')


class Attribute(Base):
    __tablename__ = 'attribute'
    id = Column(Integer, primary_key=True)
    
    name = Column(String, nullable=False)
    description = Column(String)
    double_side = Column(Boolean, default=False)

    # Unified cost structure - replaces separate constant/variable/direct tables
    cost_type = Column(SAEnum(CostType, values_callable=lambda e: [member.value for member in e], name='cost_type'),
                       nullable=False)
    cost = Column(Float, nullable=True)
    unit_id = Column(Integer, ForeignKey('unit.id'))

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    options = relationship('AttributeOption', back_populates='attribute', cascade="all, delete-orphan")
    unit = relationship('Unit', back_populates='attributes')
    nested_attribute_child = relationship('NestedAttributeChild', back_populates='attribute', cascade="all, delete-orphan")
    door_type_attribute = relationship('DoorTypeAttribute', back_populates='attribute', cascade="all, delete-orphan")
    quotation_item_attribute = relationship('QuotationItemAttribute', back_populates='attribute')


class AttributeOption(Base):
    __tablename__ = 'attribute_option'
    
    id = Column(Integer, primary_key=True)
    attribute_id = Column(Integer, ForeignKey('attribute.id'), nullable=False)
    
    name = Column(String, nullable=False)
    description = Column(String)

    # Cost fields that work for all types
    cost = Column(Float, nullable=True)

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    # Relationships
    attribute = relationship('Attribute', back_populates='options')
    quotation_item_attribute = relationship('QuotationItemAttribute', back_populates='selected_option')


class NestedAttribute(Base):
    __tablename__ = 'nested_attribute'
    
    id = Column(Integer, primary_key=True)
    
    name = Column(String, nullable=False)
    description = Column(String)

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    nested_attribute_children = relationship('NestedAttributeChild', back_populates='nested_attribute', cascade="all, delete-orphan")
    door_type_attribute = relationship('DoorTypeAttribute', back_populates='nested_attribute', cascade="all, delete-orphan")
    quotation_item_nested_attribute = relationship('QuotationItemNestedAttribute', back_populates='nested_attribute')


class NestedAttributeChild(Base):
    __tablename__ = 'nested_attribute_child'
    id = Column(Integer, primary_key=True)
    nested_attribute_id = Column(Integer, ForeignKey('nested_attribute.id'), nullable=False)
    attribute_id = Column(Integer, ForeignKey('attribute.id'), nullable=False)

    required = Column(Boolean, default=False)

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    nested_attribute = relationship('NestedAttribute', back_populates='nested_attribute_children')
    attribute = relationship('Attribute', back_populates='nested_attribute_child')


class DoorTypeAttribute(Base):
    __tablename__ = 'door_type_attribute'
    id = Column(Integer, primary_key=True)

    door_type_id = Column(Integer, ForeignKey('door_type.id', ondelete='CASCADE'), nullable=False)
    attribute_id = Column(Integer, ForeignKey('attribute.id'), nullable=True)
    nested_attribute_id = Column(Integer, ForeignKey('nested_attribute.id'), nullable=True)

    # Common fields
    required = Column(Boolean, default=False)

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    # Relationships
    attribute = relationship('Attribute', back_populates='door_type_attribute')
    door_type = relationship('DoorType', back_populates='door_type_attributes')
    nested_attribute = relationship('NestedAttribute', back_populates='door_type_attribute')

    __table_args__ = (
        UniqueConstraint('door_type_id', 'attribute_id', name='uq_door_type_attribute'),
        UniqueConstraint('door_type_id', 'nested_attribute_id', name='uq_door_type_nested_attribute')
    )


# ============================================================================
# 4. UNIT AND MEASUREMENT MANAGEMENT GROUP
# ============================================================================

class Unit(Base):
    __tablename__ = 'unit'
    
    id = Column(Integer, primary_key=True)
    
    name = Column(String, nullable=False, unique=True)
    abbreviation = Column(String, nullable=True)
    unit_type = Column(String(20), nullable=False)  # Linear or Vector
    
    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    # Backrefs
    attributes = relationship('Attribute', back_populates='unit', cascade="all, delete-orphan")
    unit_values = relationship('UnitValue', back_populates='unit')


# ============================================================================
# 5. QUOTATION MANAGEMENT GROUP
# ============================================================================
class Quotation(Base):
    __tablename__ = 'quotation'
   
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customer_details.id'), nullable=False)
    
    date = Column(Date, nullable=False, default=date.today())
    status = Column(String, default='pending')
    quotation_number = Column(String, nullable=False, unique=True)
    total_amount = Column(Float, nullable=False, default=0)
    
    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    customer = relationship('Customer', back_populates='quotations')
    items = relationship('QuotationItem', back_populates='quotation', cascade="all, delete-orphan")


class QuotationItem(Base):
    __tablename__ = 'quotation_item'
    
    id = Column(Integer, primary_key=True)
    quotation_id = Column(Integer, ForeignKey('quotation.id'), nullable=False)
    door_type_id = Column(Integer, ForeignKey('door_type.id'), nullable=False)
    thickness_option_id = Column(Integer, ForeignKey('door_type_thickness_option.id'), nullable=False)  # For cost calculation
    
    length = Column(Float, nullable=False)  # Length in inches
    breadth = Column(Float, nullable=False)  # Breadth in inches
    quantity = Column(Integer, nullable=False, default=1)
    # Cost breakdown fields
    base_cost_per_unit = Column(Float, nullable=False, default=0)  # Base door cost per unit (without attributes)
    attribute_cost_per_unit = Column(Float, nullable=False, default=0)  # Sum of attributes cost per unit
    unit_price_with_attributes = Column(Float, nullable=False, default=0)  #  per-unit price with attributes
    unit_price_with_discount = Column(Float, nullable=False, default=0)  # Per-unit price after discount, before tax
    unit_price_with_tax = Column(Float, nullable=False, default=0)  # Per-unit price after discount, before tax
    total_item_cost = Column(Float, nullable=False, default=0)  # unit_price_with_attributes * quantity

    # Tax and discount (applied in order: discount first, then tax)
    tax_percentage = Column(Float, nullable=False, default=0)  # Tax percentage applied AFTER discount
    discount_amount = Column(Float, nullable=False, default=0)  # Flat discount per unit applied BEFORE tax

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    quotation = relationship('Quotation', back_populates='items')
    door_type = relationship('DoorType', back_populates='items')
    thickness_option = relationship('DoorTypeThicknessOption', back_populates='quotation_items')  # Relationship to thickness option
    # Association object for attribute selections on this item
    attributes = relationship('QuotationItemAttribute', back_populates='quotation_item', cascade="all, delete-orphan")


class QuotationItemAttribute(Base):
    __tablename__ = 'quotation_item_attribute'
    id = Column(Integer, primary_key=True)
    quotation_item_id = Column(Integer, ForeignKey('quotation_item.id'), nullable=False)
    quotation_item_nested_attribute_id = Column(Integer, ForeignKey('quotation_item_nested_attribute.id'), nullable=True)
    attribute_id = Column(Integer, ForeignKey('attribute.id'), nullable=False)
    selected_option_id = Column(Integer, ForeignKey('attribute_option.id'), nullable=True)  # For constant_type and variable_type
    
    double_side = Column(Boolean, default=False)  # User's choice for double side
    direct_cost = Column(Float, nullable=True)  # Direct cost entered by user
    calculated_cost = Column(Float, nullable=True)  # Calculated cost from system
    total_attribute_cost = Column(Float, nullable=False, default=0)  # Total cost (direct + calculated)

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    quotation_item = relationship('QuotationItem', back_populates='attributes')
    quotation_item_nested_attribute = relationship('QuotationItemNestedAttribute', back_populates='quotation_item_attribute')
    attribute = relationship('Attribute', back_populates='quotation_item_attribute')
    selected_option = relationship('AttributeOption', back_populates='quotation_item_attribute')
    unit_values = relationship('UnitValue', back_populates='quotation_item_attribute', cascade="all, delete-orphan")


class QuotationItemNestedAttribute(Base):
    __tablename__ = 'quotation_item_nested_attribute'
    id = Column(Integer, primary_key=True)
    nested_attribute_id = Column(Integer, ForeignKey('nested_attribute.id'), nullable=False)

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    nested_attribute = relationship('NestedAttribute', back_populates='quotation_item_nested_attribute')
    quotation_item_attribute = relationship('QuotationItemAttribute', back_populates='quotation_item_nested_attribute', cascade="all, delete-orphan")


class UnitValue(Base):
    __tablename__ = 'unit_value'
    
    id = Column(Integer, primary_key=True)
    quotation_item_attribute_id = Column(Integer, ForeignKey('quotation_item_attribute.id'), nullable=False)
    unit_id = Column(Integer, ForeignKey('unit.id'), nullable=False)
    
    value1 = Column(Float, nullable=True)  # For single units (kg, piece) or length for area/linear
    value2 = Column(Float, nullable=True)  # For area units (breadth) or null for single/linear
    
    unit = relationship('Unit', back_populates='unit_values')
    quotation_item_attribute = relationship('QuotationItemAttribute', back_populates='unit_values')
