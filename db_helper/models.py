"""
Ezzy Traders Database Models
Organized by functional groups for better maintainability and understanding.

Functional Groups:
1. Employee and Role Management
2. Door and Attribute Management
3. Customer and Quotation Management
4. Unit and Measurement Management
"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, PrimaryKeyConstraint, func, Enum as SAEnum, Date, Boolean, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from datetime import date, datetime, timezone

# Import Base from base.py to avoid conflicts
from base import Base


# ============================================================================
# 1. EMPLOYEE AND ROLE MANAGEMENT GROUP
# ============================================================================

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Relationships
    employees = relationship("Employee", back_populates="role", uselist=True)
    role_permissions = relationship("RolePermission", back_populates="role", uselist=True)


class PagePermission(Base):
    __tablename__ = "page_permissions"
    id = Column(Integer, primary_key=True, index=True)
    page_name = Column(String, unique=True, index=True)
    page_path = Column(String, unique=True, index=True)
    display_name = Column(String)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Relationships
    role_permissions = relationship("RolePermission", back_populates="page", uselist=True)


class RolePermission(Base):
    __tablename__ = "role_permissions"
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"))
    page_id = Column(Integer, ForeignKey("page_permissions.id"))
    can_view = Column(Boolean, default=False)
    can_create = Column(Boolean, default=False)
    can_edit = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    can_export = Column(Boolean, default=False)
    can_import = Column(Boolean, default=False)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Relationships
    role = relationship("Role", back_populates="role_permissions")
    page = relationship("PagePermission", back_populates="role_permissions")


class Employee(Base):
    __tablename__ = "employee"
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)  # Single role assignment

    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Relationships
    role = relationship("Role", back_populates="employees")
    
    # Quotation relationships
    quotations_created = relationship('Quotation', foreign_keys='Quotation.created_by_employee_id', back_populates='created_by_employee')
    quotations_updated = relationship('Quotation', foreign_keys='Quotation.updated_by_employee_id', back_populates='updated_by_employee')


# ============================================================================
# 2. DOOR AND ATTRIBUTE MANAGEMENT GROUP
# ============================================================================



class CostType(PyEnum):
    CONSTANT = 'constant'
    VARIABLE = 'variable'
    DIRECT = 'direct'
    NESTED = 'nested'

class EntityType(PyEnum):
    DOOR = 'door'
    INVENTORY = 'inventory'
    SALES = 'sales'

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
    # One-to-many to quotation items
    items = relationship('QuotationItem', back_populates='door_type')
    # One-to-many to thickness options
    thickness_options = relationship('DoorTypeThicknessOption', back_populates='door_type')


class Attribute(Base):
    __tablename__ = 'attribute'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    double_side = Column(Boolean, default=False)
    
    # Unified cost structure - replaces separate constant/variable/direct tables
    cost_type = Column(SAEnum(CostType, values_callable=lambda e: [member.value for member in e], name='cost_type'), nullable=False)
    
    # For constant costs
    fixed_cost = Column(Numeric(10, 2))
    
    # For variable costs
    cost_per_unit = Column(Numeric(10, 2))
    unit_id = Column(Integer, ForeignKey('unit.id'))
    
    # Domain identification for future scaling
    domain = Column(SAEnum(EntityType, values_callable=lambda e: [member.value for member in e], name='domain'), default='door')
    
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


class EntityAttribute(Base):
    __tablename__ = 'entity_attribute'
    id = Column(Integer, primary_key=True)
    
    # Polymorphic relationship to any entity
    entity_type = Column(SAEnum(EntityType, values_callable=lambda e: [member.value for member in e], name='entity_type'), nullable=False)
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
    attribute_id = Column(Integer, ForeignKey('attribute.id'), nullable=False)
    relationship_order = Column(Integer, default=0)
    
    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relationships
    attribute = relationship('Attribute')
    
    __table_args__ = (
        UniqueConstraint('attribute_id', name='uq_nested_attribute'),
    )


# ============================================================================
# 3. UNIT AND MEASUREMENT MANAGEMENT GROUP
# ============================================================================

class Unit(Base):
    __tablename__ = 'unit'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    abbreviation = Column(String, nullable=True)
    unit_type = Column(String(20), nullable=False) # Linear or Vector
    is_active = Column(Boolean, default=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Backrefs
    attributes = relationship('Attribute', back_populates='unit')
    attribute_options = relationship('AttributeOption', back_populates='unit')
    unit_values = relationship('UnitValue', back_populates='unit')


class UnitValue(Base):
    __tablename__ = 'unit_value'
    id = Column(Integer, primary_key=True)
    quotation_item_attribute_id = Column(Integer, ForeignKey('quotation_item_attribute.id'), nullable=False)
    unit_id = Column(Integer, ForeignKey('unit.id'), nullable=False)
    value1 = Column(Numeric(10, 2), nullable=True)  # For single units (kg, piece) or length for area/linear
    value2 = Column(Numeric(10, 2), nullable=True)  # For area units (breadth) or null for single/linear
    unit = relationship('Unit', back_populates='unit_values')
    quotation_item_attribute = relationship('QuotationItemAttribute', back_populates='unit_values')


# ============================================================================
# 4. DOOR TYPE THICKNESS OPTIONS GROUP
# ============================================================================

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


# ============================================================================
# 5. CUSTOMER AND QUOTATION MANAGEMENT GROUP
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


class Quotation(Base):
    __tablename__ = 'quotation'
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, default=date.today())
    status = Column(String, default='pending')
    total_amount = Column(Numeric(10, 2), nullable=False, default=0)
    customer_id = Column(Integer, ForeignKey('customer_details.id'), nullable=False)
    created_by_employee_id = Column(Integer, ForeignKey('employee.id'), nullable=True)
    updated_by_employee_id = Column(Integer, ForeignKey('employee.id'), nullable=True)
    
    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    customer = relationship('Customer', back_populates='quotations')
    items = relationship('QuotationItem', back_populates='quotation')
    created_by_employee = relationship('Employee', foreign_keys=[created_by_employee_id], back_populates='quotations_created')
    updated_by_employee = relationship('Employee', foreign_keys=[updated_by_employee_id], back_populates='quotations_updated')


class QuotationItem(Base):
    __tablename__ = 'quotation_item'
    id = Column(Integer, primary_key=True)
    quotation_id = Column(Integer, ForeignKey('quotation.id'), nullable=False)
    door_type_id = Column(Integer, ForeignKey('door_type.id'), nullable=False)
    length = Column(Numeric(8, 2), nullable=False)  # Length in mm
    breadth = Column(Numeric(8, 2), nullable=False)  # Breadth in mm
    quantity = Column(Integer, nullable=False, default=1)
    price_per_unit = Column(Numeric(10, 2), nullable=False, default=0)
    total_cost = Column(Numeric(10, 2), nullable=False, default=0)
    
    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    quotation = relationship('Quotation', back_populates='items')
    door_type = relationship('DoorType', back_populates='items')
    # Association object for attribute selections on this item
    attributes = relationship('QuotationItemAttribute', back_populates='quotation_item')


class QuotationItemAttribute(Base):
    __tablename__ = 'quotation_item_attribute'
    id = Column(Integer, primary_key=True)
    quotation_item_id = Column(Integer, ForeignKey('quotation_item.id'), nullable=False)
    attribute_id = Column(Integer, ForeignKey('attribute.id'), nullable=False)
    selected_option_id = Column(Integer, nullable=True)  # For constant_type and variable_type
    double_side = Column(Boolean, default=False)  # User's choice for double side
    cost = Column(Numeric(10, 2), nullable=False, default=0)
    
    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    quotation_item = relationship('QuotationItem', back_populates='attributes')
    attribute = relationship('Attribute')
    unit_values = relationship('UnitValue', back_populates='quotation_item_attribute')
