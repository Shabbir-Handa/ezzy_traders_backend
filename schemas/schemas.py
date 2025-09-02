"""
Ezzy Traders Backend Schemas
Complete schema definitions for all entities
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from decimal import Decimal
from enum import Enum


# ============================================================================
# ENUM DEFINITIONS
# ============================================================================

class CostType(str, Enum):
    """Cost type enumeration for attributes"""
    CONSTANT = 'constant'
    VARIABLE = 'variable'
    DIRECT = 'direct'
    NESTED = 'nested'


class EntityType(str, Enum):
    """Entity type enumeration for attributes and entities"""
    DOOR = 'door'
    BOX = 'box'


# ============================================================================
# 1. EMPLOYEE MANAGEMENT SCHEMAS
# ============================================================================

class TokenData(BaseModel):
    username: str | None = None


# Employee Schemas
class EmployeeBase(BaseModel):
    username: str
    email: EmailStr
    phone: str
    first_name: str
    last_name: str
    role: str = Field(..., description="Employee role (e.g., admin, manager, sales, engineer, viewer)")
    is_active: bool = True


class EmployeeCreate(EmployeeBase):
    password: str


class EmployeeUpdate(EmployeeBase):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class EmployeeResponse(EmployeeBase):
    id: int
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmployeeLoginResponse(BaseModel):
    username: str
    email: str
    access_token: str
    token_type: str
    role: str


# ============================================================================
# 2. DOOR AND ATTRIBUTE MANAGEMENT SCHEMAS
# ============================================================================

# Unit Schemas
class UnitBase(BaseModel):
    name: str
    abbreviation: str
    unit_type: str = Field(..., description="Linear or Vector")
    is_active: bool = True


class UnitCreate(UnitBase):
    pass


class UnitUpdate(UnitBase):
    name: Optional[str] = None
    abbreviation: Optional[str] = None
    unit_type: Optional[str] = None
    is_active: Optional[bool] = None


class UnitResponse(UnitBase):
    id: int
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Door Type Schemas
class DoorTypeBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True


class DoorTypeCreate(DoorTypeBase):
    thickness_options: Optional[List["DoorTypeThicknessOptionCreate"]] = None


class DoorTypeUpdate(DoorTypeBase):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class DoorTypeResponse(DoorTypeBase):
    id: int
    entity_attributes: List["EntityAttributeResponse"] = []
    thickness_options: List["DoorTypeThicknessOptionResponse"] = []
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Door Type Thickness Option Schemas
class DoorTypeThicknessOptionBase(BaseModel):
    door_type_id: int
    thickness_value: Decimal = Field(..., description="Thickness with up to 2 decimal places")
    cost_per_sqft: Decimal = Field(..., description="Price adjustment with up to 2 decimal places")
    is_active: bool = True


class DoorTypeThicknessOptionCreate(DoorTypeThicknessOptionBase):
    pass


class DoorTypeThicknessOptionUpdate(DoorTypeThicknessOptionBase):
    door_type_id: Optional[int] = None
    thickness_value: Optional[Decimal] = None
    cost_per_sqft: Optional[Decimal] = None
    is_active: Optional[bool] = None


class DoorTypeThicknessOptionResponse(DoorTypeThicknessOptionBase):
    id: int
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Attribute Schemas
class AttributeBase(BaseModel):
    name: str
    description: Optional[str] = None
    double_side: bool = False
    cost_type: CostType = Field(..., description="Type of cost calculation")
    fixed_cost: Optional[Decimal] = Field(None, description="Fixed cost with up to 2 decimal places")
    cost_per_unit: Optional[Decimal] = Field(None, description="Cost per unit with up to 2 decimal places")
    unit_id: Optional[int] = None
    is_active: bool = True


class AttributeCreate(AttributeBase):
    options: Optional[List["AttributeOptionCreate"]] = None


class AttributeUpdate(AttributeBase):
    name: Optional[str] = None
    description: Optional[str] = None
    double_side: Optional[bool] = None
    cost_type: Optional[CostType] = None
    fixed_cost: Optional[Decimal] = None
    cost_per_unit: Optional[Decimal] = None
    unit_id: Optional[int] = None
    is_active: Optional[bool] = None


class AttributeResponse(AttributeBase):
    id: int
    options: List["AttributeOptionResponse"] = []
    unit: Optional["UnitResponse"] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Attribute Option Schemas
class AttributeOptionBase(BaseModel):
    attribute_id: int
    name: str
    description: Optional[str] = None
    cost: Decimal = Field(..., description="Cost with up to 2 decimal places")
    cost_per_unit: Optional[Decimal] = Field(None, description="Cost per unit with up to 2 decimal places")
    unit_id: Optional[int] = None
    display_order: int = 0
    is_active: bool = True


class AttributeOptionCreate(AttributeOptionBase):
    pass


class AttributeOptionUpdate(AttributeOptionBase):
    name: Optional[str] = None
    description: Optional[str] = None
    cost: Optional[Decimal] = None
    cost_per_unit: Optional[Decimal] = None
    unit_id: Optional[int] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class AttributeOptionResponse(AttributeOptionBase):
    id: int
    unit: Optional["UnitResponse"] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Entity Attribute Schemas
class EntityAttributeBase(BaseModel):
    entity_type: EntityType = Field(..., description="Type of entity")
    entity_id: int
    attribute_id: int
    required: bool = False
    order: int = 0
    custom_value: Optional[str] = None


class EntityAttributeCreate(EntityAttributeBase):
    pass


class EntityAttributeUpdate(EntityAttributeBase):
    entity_type: Optional[EntityType] = None
    entity_id: Optional[int] = None
    attribute_id: Optional[int] = None
    required: Optional[bool] = None
    order: Optional[int] = None
    custom_value: Optional[str] = None


class EntityAttributeResponse(EntityAttributeBase):
    id: int
    attribute: "AttributeResponse"
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Nested Attribute Schemas
class NestedAttributeBase(BaseModel):
    parent_attribute_id: int
    child_attribute_id: int
    relationship_order: int = 0
    is_active: bool = True


class NestedAttributeCreate(NestedAttributeBase):
    pass


class NestedAttributeUpdate(NestedAttributeBase):
    parent_attribute_id: Optional[int] = None
    child_attribute_id: Optional[int] = None
    relationship_order: Optional[int] = None
    is_active: Optional[bool] = None


class NestedAttributeResponse(NestedAttributeBase):
    id: int
    parent_attribute: "AttributeResponse"
    child_attribute: "AttributeResponse"
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# 3. CUSTOMER AND QUOTATION MANAGEMENT SCHEMAS
# ============================================================================

# Customer Schemas
class CustomerBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    is_active: bool = True


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(CustomerBase):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    is_active: Optional[bool] = None


class CustomerResponse(CustomerBase):
    id: int
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Quotation Schemas
class QuotationBase(BaseModel):
    customer_id: int
    date: datetime
    status: str = Field(default="pending", description="draft, sent, accepted, rejected, expired")


class QuotationCreate(QuotationBase):
    items: Optional[List["QuotationItemCreate"]] = None


class QuotationUpdate(QuotationBase):
    customer_id: Optional[int] = None
    date: Optional[datetime] = None
    status: Optional[str] = None


class QuotationResponse(QuotationBase):
    id: int
    total_amount: Optional[Decimal] = None
    customer: "CustomerResponse"
    items: List["QuotationItemResponse"] = []
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Quotation Item Schemas
class QuotationItemBase(BaseModel):
    quotation_id: int
    door_type_id: int
    thickness_option_id: int
    quantity: int = 1
    length: Decimal = Field(..., description="Length with up to 2 decimal places")
    breadth: Decimal = Field(..., description="Breadth with up to 2 decimal places")


class QuotationItemCreate(QuotationItemBase):
    quotation_id: Optional[int] = None  # Optional when creating
    attributes: Optional[List["QuotationItemAttributeCreate"]] = None


class QuotationItemUpdate(QuotationItemBase):
    quotation_id: Optional[int] = None
    door_type_id: Optional[int] = None
    thickness_option_id: Optional[int] = None
    quantity: Optional[int] = None
    length: Optional[Decimal] = None
    breadth: Optional[Decimal] = None


class QuotationItemResponse(QuotationItemBase):
    id: int
    door_type: "DoorTypeResponse"
    thickness_option: Optional["DoorTypeThicknessOptionResponse"] = None
    attributes: List["QuotationItemAttributeResponse"] = []
    base_cost_per_unit: Optional[Decimal] = None
    attribute_cost_per_unit: Optional[Decimal] = None
    unit_price_with_attributes: Optional[Decimal] = None
    total_item_cost: Optional[Decimal] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Quotation Item Attribute Schemas
class QuotationItemAttributeBase(BaseModel):
    quotation_item_id: int
    attribute_id: int
    selected_option_id: Optional[int] = None
    double_side: bool = False
    direct_cost: Optional[Decimal] = Field(None, description="Direct cost entered by user for this attribute")


class QuotationItemAttributeCreate(QuotationItemAttributeBase):
    quotation_item_id: Optional[int] = None  # Optional when creating
    unit_values: Optional[List["UnitValueCreate"]] = None


class QuotationItemAttributeUpdate(QuotationItemAttributeBase):
    quotation_item_id: Optional[int] = None
    attribute_id: Optional[int] = None
    double_side: Optional[bool] = None
    direct_cost: Optional[Decimal] = None


class QuotationItemAttributeResponse(QuotationItemAttributeBase):
    id: int
    attribute: "AttributeResponse"
    calculated_cost: Optional[Decimal] = None
    total_attribute_cost: Optional[Decimal] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    
class UnitValueBase(BaseModel):
    quotation_item_attribute_id: int
    unit_id: int
    value1: Optional[Decimal] = Field(None, description="Value1 with up to 2 decimal places")
    value2: Optional[Decimal] = Field(None, description="Value2 with up to 2 decimal places")


class UnitValueCreate(UnitValueBase):
    quotation_item_attribute_id: Optional[int] = None


class UnitValueUpdate(UnitValueBase):
    quotation_item_attribute_id: Optional[int] = None
    unit_id: Optional[int] = None
    value1: Optional[Decimal] = None
    value2: Optional[Decimal] = None


class UnitValueResponse(UnitValueBase):
    id: int
    unit: Optional["UnitResponse"] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# 4. COMMON RESPONSE SCHEMAS
# ============================================================================

class IDShortResponse(BaseModel):
    id: int


class MessageResponse(BaseModel):
    message: str


class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    size: int
    pages: int

# ============================================================================
# FORWARD REFERENCE RESOLUTION
# ============================================================================

# Update forward references for all schemas that reference each other
# DoorTypeCreate.model_rebuild()
# DoorTypeResponse.model_rebuild()
# AttributeCreate.model_rebuild()
# AttributeResponse.model_rebuild()
# EntityAttributeResponse.model_rebuild()
# NestedAttributeResponse.model_rebuild()
# QuotationCreate.model_rebuild()
# QuotationResponse.model_rebuild()
# QuotationItemCreate.model_rebuild()
# QuotationItemResponse.model_rebuild()
# QuotationItemAttributeCreate.model_rebuild()
# QuotationItemAttributeResponse.model_rebuild()
# UnitValueResponse.model_rebuild()
