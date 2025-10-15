"""
Ezzy Traders Backend Schemas
Complete schema definitions for all entities
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from enum import Enum


# ============================================================================
# ENUM DEFINITIONS
# ============================================================================

class CostType(str, Enum):
    """Cost type enumeration for attributes"""
    CONSTANT = 'constant'
    VARIABLE = 'variable'
    DIRECT = 'direct'


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
    role: str


class EmployeeCreate(EmployeeBase):
    password: str


class EmployeeUpdate(EmployeeBase):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None


class EmployeeResponse(EmployeeBase):
    id: int
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

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
    unit_type: str


class UnitCreate(UnitBase):
    pass


class UnitUpdate(UnitBase):
    name: Optional[str] = None
    abbreviation: Optional[str] = None
    unit_type: Optional[str] = None


class UnitResponse(UnitBase):
    id: int
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Door Type Schemas
class DoorTypeBase(BaseModel):
    name: str
    description: Optional[str] = None


class DoorTypeCreate(DoorTypeBase):
    thickness_options: Optional[List["DoorTypeThicknessOptionCreate"]] = None


class DoorTypeUpdate(DoorTypeBase):
    name: Optional[str] = None
    description: Optional[str] = None


class DoorTypeResponse(DoorTypeBase):
    id: int
    door_type_attributes: List["DoorTypeAttributeResponse"] = []
    thickness_options: List["DoorTypeThicknessOptionResponse"] = []
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DoorTypeShortResponse(DoorTypeBase):
    id: int

    class Config:
        from_attributes = True

# Door Type Thickness Option Schemas
class DoorTypeThicknessOptionBase(BaseModel):
    door_type_id: int
    thickness_value: float
    cost_per_sqft: float


class DoorTypeThicknessOptionCreate(DoorTypeThicknessOptionBase):
    door_type_id: Optional[int] = None


class DoorTypeThicknessOptionUpdate(DoorTypeThicknessOptionBase):
    door_type_id: Optional[int] = None
    thickness_value: Optional[float] = None
    cost_per_sqft: Optional[float] = None


class DoorTypeThicknessOptionResponse(DoorTypeThicknessOptionBase):
    id: int
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Attribute Schemas
class AttributeBase(BaseModel):
    name: str
    description: Optional[str] = None
    double_side: bool = False
    cost_type: CostType
    cost: Optional[float] = None
    unit_id: Optional[int] = None


class AttributeCreate(AttributeBase):
    has_options: bool = False
    options: Optional[List["AttributeOptionCreate"]] = None


class AttributeUpdate(AttributeBase):
    name: Optional[str] = None
    description: Optional[str] = None
    double_side: Optional[bool] = None
    cost_type: Optional[CostType] = None
    cost: Optional[float] = None
    unit_id: Optional[int] = None


class AttributeResponse(AttributeBase):
    id: int
    options: List["AttributeOptionResponse"] = []
    unit: Optional["UnitResponse"] = None
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AttributeShortResponse(AttributeBase):
    id: int

    class Config:
        from_attributes = True


class AttributeListResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    double_side: bool
    cost_type: CostType
    cost: Optional[float] = None
    unit_id: Optional[int] = None

    class Config:
        from_attributes = True


# Attribute Option Schemas
class AttributeOptionBase(BaseModel):
    attribute_id: int
    name: str
    description: Optional[str] = None
    cost: Optional[float] = None


class AttributeOptionCreate(AttributeOptionBase):
    attribute_id: Optional[int] = None


class AttributeOptionUpdate(AttributeOptionBase):
    name: Optional[str] = None
    description: Optional[str] = None
    cost: Optional[float] = None


class AttributeOptionResponse(AttributeOptionBase):
    id: int
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Door Type Attribute Schemas
class DoorTypeAttributeBase(BaseModel):
    door_type_id: int
    attribute_id: Optional[int] = None
    nested_attribute_id: Optional[int] = None
    required: bool = False


class DoorTypeAttributeCreate(DoorTypeAttributeBase):
    pass


class DoorTypeAttributeUpdate(DoorTypeAttributeBase):
    door_type_id: Optional[int] = None
    attribute_id: Optional[int] = None
    nested_attribute_id: Optional[int] = None
    required: Optional[bool] = None


class DoorTypeAttributeResponse(DoorTypeAttributeBase):
    id: int
    attribute: Optional["AttributeResponse"] = None
    nested_attribute: Optional["NestedAttributeResponse"] = None
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Nested Attribute Schemas
class NestedAttributeBase(BaseModel):
    name: str
    description: Optional[str] = None


class NestedAttributeCreate(NestedAttributeBase):
    children: Optional[List["NestedAttributeChildCreate"]] = None


class NestedAttributeUpdate(NestedAttributeBase):
    name: Optional[str] = None
    description: Optional[str] = None


class NestedAttributeShortResponse(NestedAttributeBase):
    id: int

    class Config:
        from_attributes = True


class NestedAttributeResponse(NestedAttributeShortResponse):
    children: List["NestedAttributeChildResponse"] = []
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NestedAttributeChildBase(BaseModel):
    nested_attribute_id: int
    attribute_id: int
    required: bool = False


class NestedAttributeChildCreate(NestedAttributeChildBase):
    nested_attribute_id: Optional[int] = None


class NestedAttributeChildUpdate(NestedAttributeChildBase):
    nested_attribute_id: Optional[int] = None
    attribute_id: Optional[int] = None
    required: Optional[bool] = None


class NestedAttributeChildResponse(NestedAttributeChildBase):
    id: int
    attribute: Optional["AttributeResponse"] = None
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

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


class CustomerResponse(CustomerBase):
    id: int
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Quotation Schemas
class QuotationBase(BaseModel):
    customer_id: int
    date: datetime
    status: str


class QuotationCreate(QuotationBase):
    items: Optional[List["QuotationItemCreate"]] = None


class QuotationUpdate(QuotationBase):
    customer_id: Optional[int] = None
    date: Optional[datetime] = None
    status: Optional[str] = None


class QuotationResponse(QuotationBase):
    id: int
    quotation_number: str
    total_amount: Optional[float] = None
    customer: "CustomerResponse"
    items: List["QuotationItemResponse"] = None
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuotationShortResponse(QuotationBase):
    id: int
    quotation_number: str
    total_amount: Optional[float] = None
    customer: "CustomerResponse"
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime


# Quotation Item Schemas
class QuotationItemBase(BaseModel):
    quotation_id: int
    door_type_id: int
    thickness_option_id: int
    quantity: int = 1
    length: float
    breadth: float
    tax_percentage: Optional[float] = None
    discount_amount: Optional[float] = None


class QuotationItemCreate(QuotationItemBase):
    quotation_id: Optional[int] = None  # Optional when creating
    attributes: Optional[List["QuotationItemAttributeCreate"]] = None
    nested_attributes: Optional[List["QuotationItemNestedAttributeCreate"]] = None


class QuotationItemUpdate(QuotationItemBase):
    quotation_id: Optional[int] = None
    door_type_id: Optional[int] = None
    thickness_option_id: Optional[int] = None
    quantity: Optional[int] = None
    length: Optional[float] = None
    breadth: Optional[float] = None


class QuotationItemResponse(QuotationItemBase):
    id: int
    door_type: "DoorTypeShortResponse"
    thickness_option: Optional["DoorTypeThicknessOptionResponse"] = None
    attributes: List["QuotationItemAttributeResponse"] = None
    base_cost_per_unit: Optional[float] = None
    attribute_cost_per_unit: Optional[float] = None
    unit_price_with_attributes: Optional[float] = None  # Price with attributes
    unit_price_with_discount: Optional[float] = None  # Price after discount, before tax
    unit_price_with_tax: Optional[float] = None  # Price after discount and tax
    total_item_cost: Optional[float] = None
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Quotation Item Attribute Schemas
class QuotationItemAttributeBase(BaseModel):
    quotation_item_id: int
    quotation_item_nested_attribute_id: Optional[int] = None
    attribute_id: int
    selected_option_id: Optional[int] = None
    double_side: bool = False
    direct_cost: Optional[float] = None


class QuotationItemAttributeCreate(QuotationItemAttributeBase):
    quotation_item_id: Optional[int] = None  # Optional when creating
    unit_values: Optional[List["UnitValueCreate"]] = None


class QuotationItemAttributeUpdate(QuotationItemAttributeBase):
    quotation_item_id: Optional[int] = None
    quotation_item_nested_attribute_id: Optional[int] = None
    attribute_id: Optional[int] = None
    double_side: Optional[bool] = None
    direct_cost: Optional[float] = None


class QuotationItemAttributeResponse(QuotationItemAttributeBase):
    id: int
    quotation_item_nested_attribute: Optional["QuotationItemNestedAttributeResponse"] = None
    attribute: "AttributeShortResponse"
    selected_option: Optional["AttributeOptionResponse"] = None
    unit_values: List["UnitValueResponse"] = None
    calculated_cost: Optional[float] = None
    total_attribute_cost: Optional[float] = None
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuotationItemNestedAttributeCreate(BaseModel):
    nested_attribute_id: int
    attributes: Optional[List["QuotationItemAttributeCreate"]] = None


class QuotationItemNestedAttributeResponse(BaseModel):
    id: int
    nested_attribute: Optional["NestedAttributeShortResponse"] = None
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    
class UnitValueBase(BaseModel):
    quotation_item_attribute_id: int
    unit_id: int
    value1: Optional[float] = None
    value2: Optional[float] = None


class UnitValueCreate(UnitValueBase):
    quotation_item_attribute_id: Optional[int] = None


class UnitValueUpdate(UnitValueBase):
    quotation_item_attribute_id: Optional[int] = None
    unit_id: Optional[int] = None
    value1: Optional[float] = None
    value2: Optional[float] = None


class UnitValueResponse(UnitValueBase):
    id: int
    unit: Optional["UnitResponse"] = None

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
# 5. PAGINATION RESPONSE SCHEMAS WITH INHERITANCE
# ============================================================================

class PaginatedDoorTypeResponse(BaseModel):
    data: List["DoorTypeResponse"]
    total: int
    page: int
    size: int
    pages: int


class PaginatedAttributeResponse(BaseModel):
    data: List["AttributeResponse"]
    total: int
    page: int
    size: int
    pages: int


class PaginatedNestedAttributeResponse(BaseModel):
    data: List["NestedAttributeResponse"]
    total: int
    page: int
    size: int
    pages: int


class PaginatedUnitResponse(BaseModel):
    data: List["UnitResponse"]
    total: int
    page: int
    size: int
    pages: int


class PaginatedCustomerResponse(BaseModel):
    data: List["CustomerResponse"]
    total: int
    page: int
    size: int
    pages: int


class PaginatedQuotationShortResponse(BaseModel):
    data: List["QuotationShortResponse"]
    total: int
    page: int
    size: int
    pages: int


class PaginatedEmployeeResponse(BaseModel):
    data: List["EmployeeResponse"]
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
