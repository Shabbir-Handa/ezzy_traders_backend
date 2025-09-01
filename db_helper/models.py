"""
Ezzy Traders Database Models
Organized by functional groups for better maintainability and understanding.

Functional Groups:
1. Employee Management
2. Door and Attribute Management
3. Customer and Quotation Management
4. Unit and Measurement Management
"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, PrimaryKeyConstraint, func, \
    Enum as SAEnum, Date, Boolean, CheckConstraint, UniqueConstraint, and_
from sqlalchemy.orm import relationship, foreign
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum as PyEnum
from datetime import date, datetime, timezone

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
    is_active = Column(Boolean, default=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))


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
    
    is_active = Column(Boolean, default=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    quotations = relationship('Quotation', back_populates='customer')


# ============================================================================
# 3. DOOR AND ATTRIBUTE MANAGEMENT GROUP
# ============================================================================

class CostType(PyEnum):
    CONSTANT = 'constant'
    VARIABLE = 'variable'
    DIRECT = 'direct'
    NESTED = 'nested'


class EntityType(PyEnum):
    DOOR = 'door'
    BOX = 'box'  


class DoorType(Base):
    __tablename__ = 'door_type'
    
    id = Column(Integer, primary_key=True)
    
    name = Column(String, nullable=False)
    description = Column(String)
    
    is_active = Column(Boolean, default=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Many-to-many with Attribute via EntityAttribute
    attributes = relationship(
        'Attribute',
        secondary='entity_attribute',
        primaryjoin="and_(EntityAttribute.entity_type == 'door', EntityAttribute.entity_id == DoorType.id)",
        secondaryjoin="EntityAttribute.attribute_id == Attribute.id",
        back_populates='door_types'
    )

    entity_attributes = relationship(
        'EntityAttribute',
        primaryjoin=lambda: and_(
            foreign(EntityAttribute.entity_id) == DoorType.id,
            EntityAttribute.entity_type == 'door'
        ),
        order_by='EntityAttribute.order'
    )

    # One-to-many to quotation items
    items = relationship('QuotationItem', back_populates='door_type')
    # One-to-many to thickness options
    thickness_options = relationship('DoorTypeThicknessOption', back_populates='door_type')


class DoorTypeThicknessOption(Base):
    __tablename__ = 'door_type_thickness_option'
    
    id = Column(Integer, primary_key=True)
    door_type_id = Column(Integer, ForeignKey('door_type.id'), nullable=False)
    
    thickness_value = Column(Numeric(5, 2), nullable=False)  # Thickness in mm
    cost_per_sqft = Column(Numeric(10, 2), nullable=False)  # Cost per square foot for this thickness
    
    is_active = Column(Boolean, default=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    door_type = relationship('DoorType', back_populates='thickness_options')


class Attribute(Base):
    __tablename__ = 'attribute'
    id = Column(Integer, primary_key=True)
    
    name = Column(String, nullable=False)
    description = Column(String)
    double_side = Column(Boolean, default=False)

    # Unified cost structure - replaces separate constant/variable/direct tables
    cost_type = Column(SAEnum(CostType, values_callable=lambda e: [member.value for member in e], name='cost_type'),
                       nullable=False)

    # For constant costs
    fixed_cost = Column(Numeric(10, 2))

    # For variable costs
    cost_per_unit = Column(Numeric(10, 2))
    unit_id = Column(Integer, ForeignKey('unit.id'))

    # Audit fields
    is_active = Column(Boolean, default=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Single options relationship for all types
    options = relationship('AttributeOption', back_populates='attribute')

    # Many-to-many with DoorType via EntityAttribute
    door_types = relationship(
        'DoorType',
        secondary='entity_attribute',
        primaryjoin="and_(EntityAttribute.entity_type == 'door', EntityAttribute.attribute_id == Attribute.id)",
        secondaryjoin="EntityAttribute.entity_id == DoorType.id",
        back_populates='attributes'
    )

    # Unit relationship
    unit = relationship('Unit', back_populates='attributes')

    __table_args__ = (
        # Ensure cost fields are properly used based on cost_type
        CheckConstraint(
            "(cost_type = 'constant' AND fixed_cost IS NOT NULL) OR "
            "(cost_type = 'variable' AND cost_per_unit IS NOT NULL) OR "
            "(cost_type = 'direct') OR "
            "(cost_type = 'nested')",
            name='check_cost_fields_usage'
        ),
    )


class AttributeOption(Base):
    __tablename__ = 'attribute_option'
    
    id = Column(Integer, primary_key=True)
    attribute_id = Column(Integer, ForeignKey('attribute.id'), nullable=False)
    
    name = Column(String, nullable=False)
    description = Column(String)

    # Cost fields that work for all types
    cost = Column(Numeric(10, 2), nullable=False, default=0)
    cost_per_unit = Column(Numeric(10, 2))
    unit_id = Column(Integer, ForeignKey('unit.id'))

    # For ordering options
    display_order = Column(Integer, default=0)

    # Audit fields
    is_active = Column(Boolean, default=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Relationships
    attribute = relationship('Attribute', back_populates='options')
    unit = relationship('Unit')

    __table_args__ = (
        # Ensure at least one cost field is provided
        CheckConstraint('cost > 0 OR cost_per_unit > 0', name='check_cost_provided'),
    )


class NestedAttribute(Base):
    __tablename__ = 'nested_attribute'
    
    id = Column(Integer, primary_key=True)
    
    # Parent attribute (the main component)
    parent_attribute_id = Column(Integer, ForeignKey('attribute.id'), nullable=False)
    
    # Child attribute (the nested component)
    child_attribute_id = Column(Integer, ForeignKey('attribute.id'), nullable=False)
    
    relationship_order = Column(Integer, default=0)

    # Audit fields
    is_active = Column(Boolean, default=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Relationships
    parent_attribute = relationship('Attribute', foreign_keys=[parent_attribute_id])
    child_attribute = relationship('Attribute', foreign_keys=[child_attribute_id])

    __table_args__ = (
        UniqueConstraint('parent_attribute_id', 'child_attribute_id', name='uq_parent_child_attribute'),
    )


class EntityAttribute(Base):
    __tablename__ = 'entity_attribute'
    id = Column(Integer, primary_key=True)

    # Polymorphic relationship to any entity
    entity_type = Column(
        SAEnum(EntityType, values_callable=lambda e: [member.value for member in e], name='entity_type'),
        nullable=False)
    entity_id = Column(Integer, nullable=False)
    attribute_id = Column(Integer, ForeignKey('attribute.id'), nullable=False)

    # Common fields
    required = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    custom_value = Column(String)  # For domain-specific overrides

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Relationships
    attribute = relationship('Attribute')

    __table_args__ = (
        UniqueConstraint('entity_type', 'entity_id', 'attribute_id', name='uq_entity_attribute'),
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
    
    is_active = Column(Boolean, default=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Backrefs
    attributes = relationship('Attribute', back_populates='unit')
    attribute_options = relationship('AttributeOption', back_populates='unit')
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
    total_amount = Column(Numeric(10, 2), nullable=False, default=0)
    
    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    customer = relationship('Customer', back_populates='quotations')
    items = relationship('QuotationItem', back_populates='quotation')


class QuotationItem(Base):
    __tablename__ = 'quotation_item'
    
    id = Column(Integer, primary_key=True)
    quotation_id = Column(Integer, ForeignKey('quotation.id'), nullable=False)
    door_type_id = Column(Integer, ForeignKey('door_type.id'), nullable=False)
    thickness_option_id = Column(Integer, ForeignKey('door_type_thickness_option.id'), nullable=False)  # For cost calculation
    
    length = Column(Numeric(8, 2), nullable=False)  # Length in mm
    breadth = Column(Numeric(8, 2), nullable=False)  # Breadth in mm
    quantity = Column(Integer, nullable=False, default=1)
    # Cost breakdown fields
    base_cost_per_unit = Column(Numeric(10, 2), nullable=False, default=0)  # Base door cost per unit (without attributes)
    attribute_cost_per_unit = Column(Numeric(10, 2), nullable=False, default=0)  # Sum of attributes cost per unit
    unit_price_with_attributes = Column(Numeric(10, 2), nullable=False, default=0)  # Per-door price including attributes
    total_item_cost = Column(Numeric(12, 2), nullable=False, default=0)  # unit_price_with_attributes * quantity

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    quotation = relationship('Quotation', back_populates='items')
    door_type = relationship('DoorType', back_populates='items')
    thickness_option = relationship('DoorTypeThicknessOption', backref='quotation_items')  # Relationship to thickness option
    # Association object for attribute selections on this item
    attributes = relationship('QuotationItemAttribute', back_populates='quotation_item')


class QuotationItemAttribute(Base):
    __tablename__ = 'quotation_item_attribute'
    id = Column(Integer, primary_key=True)
    quotation_item_id = Column(Integer, ForeignKey('quotation_item.id'), nullable=False)
    attribute_id = Column(Integer, ForeignKey('attribute.id'), nullable=False)
    selected_option_id = Column(Integer, nullable=True)  # For constant_type and variable_type
    
    double_side = Column(Boolean, default=False)  # User's choice for double side
    direct_cost = Column(Numeric(10, 2), nullable=True)  # Direct cost entered by user
    calculated_cost = Column(Numeric(10, 2), nullable=True)  # Calculated cost from system
    total_attribute_cost = Column(Numeric(10, 2), nullable=False, default=0)  # Total cost (direct + calculated)

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    quotation_item = relationship('QuotationItem', back_populates='attributes')
    attribute = relationship('Attribute')
    unit_values = relationship('UnitValue', back_populates='quotation_item_attribute')


class UnitValue(Base):
    __tablename__ = 'unit_value'
    
    id = Column(Integer, primary_key=True)
    quotation_item_attribute_id = Column(Integer, ForeignKey('quotation_item_attribute.id'), nullable=False)
    unit_id = Column(Integer, ForeignKey('unit.id'), nullable=False)
    
    value1 = Column(Numeric(10, 2), nullable=True)  # For single units (kg, piece) or length for area/linear
    value2 = Column(Numeric(10, 2), nullable=True)  # For area units (breadth) or null for single/linear
    
    unit = relationship('Unit', back_populates='unit_values')
    quotation_item_attribute = relationship('QuotationItemAttribute', back_populates='unit_values')
