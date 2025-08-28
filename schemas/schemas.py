"""
Ezzy Traders Backend Schemas
Complete schema definitions for all entities
"""

from datetime import datetime
from typing import Optional, List, Annotated, ForwardRef
from pydantic import BaseModel, EmailStr, Field, field_validator
from decimal import Decimal


# ============================================================================
# 1. EMPLOYEE AND ROLE MANAGEMENT SCHEMAS
# ============================================================================

class TokenData(BaseModel):
    username: str | None = None


# Role Schemas
class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class RoleResponse(RoleBase):
    id: int
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Page Permission Schemas
class PagePermissionBase(BaseModel):
    page_name: str
    page_path: str
    display_name: str
    description: Optional[str] = None
    is_active: bool = True


class PagePermissionCreate(PagePermissionBase):
    pass


class PagePermissionUpdate(PagePermissionBase):
    page_name: Optional[str] = None
    page_path: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PagePermissionResponse(PagePermissionBase):
    id: int
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Role Permission Schemas
class RolePermissionBase(BaseModel):
    role_id: int
    page_id: int
    can_view: bool = False
    can_create: bool = False
    can_edit: bool = False
    can_delete: bool = False
    can_export: bool = False
    can_import: bool = False


class RolePermissionCreate(RolePermissionBase):
    pass


class RolePermissionUpdate(RolePermissionBase):
    role_id: Optional[int] = None
    page_id: Optional[int] = None
    can_view: Optional[bool] = None
    can_create: Optional[bool] = None
    can_edit: Optional[bool] = None
    can_delete: Optional[bool] = None
    can_export: Optional[bool] = None
    can_import: Optional[bool] = None


class RolePermissionResponse(RolePermissionBase):
    id: int
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Employee Schemas
class EmployeeBase(BaseModel):
    username: str
    email: EmailStr
    phone: str
    first_name: str
    last_name: str
    role_id: Optional[int] = None
    is_active: bool = True


class EmployeeCreate(EmployeeBase):
    password: str


class EmployeeUpdate(EmployeeBase):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None


class EmployeeResponse(EmployeeBase):
    id: int
    role: Optional[RoleResponse] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Authentication Schemas
class EmployeeLogin(BaseModel):
    username: str
    password: str


class EmployeeLoginResponse(BaseModel):
    username: str
    email: str
    access_token: str
    token_type: str
    permissions: List[dict] = []
    role: Optional[RoleResponse] = None


# Permission Response Schemas
class PageInfo(BaseModel):
    page_id: int
    page_name: str
    page_path: str
    display_name: str
    permissions: dict


class UserPermissions(BaseModel):
    user_id: int
    username: str
    role: Optional[RoleResponse] = None
    pages: List[PageInfo] = []


# ============================================================================
# 2. DOOR AND ATTRIBUTE MANAGEMENT SCHEMAS
# ============================================================================

# Unit Schemas
class UnitBase(BaseModel):
    name: str
    symbol: str
    description: Optional[str] = None
    is_active: bool = True


class UnitCreate(UnitBase):
    pass


class UnitUpdate(UnitBase):
    name: Optional[str] = None
    symbol: Optional[str] = None
    description: Optional[str] = None
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
    base_price: Decimal = Field(..., description="Base price with up to 2 decimal places")
    is_active: bool = True

    @field_validator('base_price')
    @classmethod
    def validate_decimal_places(cls, v):
        if v is not None:
            # Round to 2 decimal places
            return round(v, 2)
        return v


class DoorTypeCreate(DoorTypeBase):
    pass


class DoorTypeUpdate(DoorTypeBase):
    name: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[Decimal] = None
    is_active: Optional[bool] = None


class DoorTypeResponse(DoorTypeBase):
    id: int
    attributes: List["EntityAttributeResponse"] = []
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
    thickness: Decimal = Field(..., description="Thickness with up to 2 decimal places")
    price_adjustment: Decimal = Field(..., description="Price adjustment with up to 2 decimal places")
    is_active: bool = True

    @field_validator('thickness', 'price_adjustment')
    @classmethod
    def validate_decimal_places(cls, v):
        if v is not None:
            # Round to 2 decimal places
            return round(v, 2)
        return v


class DoorTypeThicknessOptionCreate(DoorTypeThicknessOptionBase):
    pass


class DoorTypeThicknessOptionUpdate(DoorTypeThicknessOptionBase):
    thickness: Optional[Decimal] = None
    price_adjustment: Optional[Decimal] = None
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
    cost_type: str = Field(..., description="constant, variable, direct, or nested")
    fixed_cost: Optional[Decimal] = Field(None, description="Fixed cost with up to 2 decimal places")
    cost_per_unit: Optional[Decimal] = Field(None, description="Cost per unit with up to 2 decimal places")
    unit_id: Optional[int] = None
    domain: str = Field(default="door", description="door, inventory, sales")
    is_active: bool = True

    @field_validator('fixed_cost', 'cost_per_unit')
    @classmethod
    def validate_decimal_places(cls, v):
        if v is not None:
            # Round to 2 decimal places
            return round(v, 2)
        return v


class AttributeCreate(AttributeBase):
    pass


class AttributeUpdate(AttributeBase):
    name: Optional[str] = None
    description: Optional[str] = None
    double_side: Optional[bool] = None
    cost_type: Optional[str] = None
    fixed_cost: Optional[Decimal] = None
    cost_per_unit: Optional[Decimal] = None
    unit_id: Optional[int] = None
    domain: Optional[str] = None
    is_active: Optional[bool] = None


class AttributeResponse(AttributeBase):
    id: int
    options: List["AttributeOptionResponse"] = []
    unit: Optional[UnitResponse] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Attribute Option Schemas
class AttributeOptionBase(BaseModel):
    attribute_id: int
    value: str
    cost_adjustment: Decimal = Field(..., description="Cost adjustment with up to 2 decimal places")
    is_active: bool = True

    @field_validator('cost_adjustment')
    @classmethod
    def validate_decimal_places(cls, v):
        if v is not None:
            # Round to 2 decimal places
            return round(v, 2)
        return v


class AttributeOptionCreate(AttributeOptionBase):
    pass


class AttributeOptionUpdate(AttributeOptionBase):
    value: Optional[str] = None
    cost_adjustment: Optional[Decimal] = None
    is_active: Optional[bool] = None


class AttributeOptionResponse(AttributeOptionBase):
    id: int
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Entity Attribute Schemas
class EntityAttributeBase(BaseModel):
    entity_type: str = Field(..., description="door, inventory, sales")
    entity_id: int
    attribute_id: int
    required: bool = False
    order: int = 0
    custom_value: Optional[str] = None
    is_active: bool = True


class EntityAttributeCreate(EntityAttributeBase):
    pass


class EntityAttributeUpdate(EntityAttributeBase):
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    attribute_id: Optional[int] = None
    required: Optional[bool] = None
    order: Optional[int] = None
    custom_value: Optional[str] = None
    is_active: Optional[bool] = None


class EntityAttributeResponse(EntityAttributeBase):
    id: int
    attribute: AttributeResponse
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Nested Attribute Schemas
class NestedAttributeBase(BaseModel):
    attribute_id: int
    nested_attribute_id: int
    quantity: int = 1
    is_active: bool = True


class NestedAttributeCreate(NestedAttributeBase):
    pass


class NestedAttributeUpdate(NestedAttributeBase):
    nested_attribute_id: Optional[int] = None
    quantity: Optional[int] = None
    is_active: Optional[bool] = None


class NestedAttributeResponse(NestedAttributeBase):
    id: int
    nested_attribute: AttributeResponse
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


# Quotation Item Attribute Schemas (for comprehensive creation)
class QuotationItemAttributeCreateSimple(BaseModel):
    attribute_id: int
    value: str
    cost_adjustment: Optional[Decimal] = Field(None, description="Cost adjustment with up to 2 decimal places")

    @field_validator('cost_adjustment')
    @classmethod
    def validate_decimal_places(cls, v):
        if v is not None:
            # Round to 2 decimal places
            return round(v, 2)
        return v


# Quotation Item Schemas (for comprehensive creation)
class QuotationItemCreateSimple(BaseModel):
    door_type_id: int
    quantity: int = 1
    width: Optional[Decimal] = Field(None, description="Width with up to 2 decimal places")
    height: Optional[Decimal] = Field(None, description="Height with up to 2 decimal places")
    thickness: Optional[Decimal] = Field(None, description="Thickness with up to 2 decimal places")
    notes: Optional[str] = None
    attributes: List[QuotationItemAttributeCreateSimple] = []

    @field_validator('width', 'height', 'thickness')
    @classmethod
    def validate_decimal_places(cls, v):
        if v is not None:
            # Round to 2 decimal places
            return round(v, 2)
        return v


# Comprehensive Quotation Creation Schema
class ComprehensiveQuotationCreate(BaseModel):
    customer_id: int
    quotation_number: Optional[str] = None
    quotation_date: datetime
    valid_until: Optional[datetime] = None
    status: str = Field(default="draft", description="draft, sent, accepted, rejected, expired")
    notes: Optional[str] = None
    created_by_employee_id: Optional[int] = None
    updated_by_employee_id: Optional[int] = None
    items: List[QuotationItemCreateSimple]


# Quotation Schemas
class QuotationBase(BaseModel):
    customer_id: int
    quotation_number: Optional[str] = None
    quotation_date: datetime
    valid_until: Optional[datetime] = None
    total_amount: Optional[Decimal] = Field(None, description="Total amount with up to 2 decimal places")
    status: str = Field(default="draft", description="draft, sent, accepted, rejected, expired")
    notes: Optional[str] = None
    created_by_employee_id: Optional[int] = None
    updated_by_employee_id: Optional[int] = None
    is_active: bool = True

    @field_validator('total_amount')
    @classmethod
    def validate_decimal_places(cls, v):
        if v is not None:
            # Round to 2 decimal places
            return round(v, 2)
        return v


class QuotationCreate(QuotationBase):
    pass


class QuotationUpdate(QuotationBase):
    customer_id: Optional[int] = None
    quotation_number: Optional[str] = None
    quotation_date: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    total_amount: Optional[Decimal] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    created_by_employee_id: Optional[int] = None
    updated_by_employee_id: Optional[int] = None
    is_active: Optional[bool] = None


class QuotationResponse(QuotationBase):
    id: int
    customer: CustomerResponse
    items: List["QuotationItemResponse"] = []
    created_by_employee: Optional[EmployeeResponse] = None
    updated_by_employee: Optional[EmployeeResponse] = None
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
    quantity: int = 1
    unit_price: Optional[Decimal] = Field(None, description="Unit price with up to 2 decimal places")
    total_price: Optional[Decimal] = Field(None, description="Total price with up to 2 decimal places")
    width: Optional[Decimal] = Field(None, description="Width with up to 2 decimal places")
    height: Optional[Decimal] = Field(None, description="Height with up to 2 decimal places")
    thickness: Optional[Decimal] = Field(None, description="Thickness with up to 2 decimal places")
    notes: Optional[str] = None
    is_active: bool = True

    @field_validator('unit_price', 'total_price', 'width', 'height', 'thickness')
    @classmethod
    def validate_decimal_places(cls, v):
        if v is not None:
            # Round to 2 decimal places
            return round(v, 2)
        return v


class QuotationItemCreate(QuotationItemBase):
    pass


class QuotationItemUpdate(QuotationItemBase):
    quotation_id: Optional[int] = None
    door_type_id: Optional[int] = None
    quantity: Optional[int] = None
    unit_price: Optional[Decimal] = None
    total_price: Optional[Decimal] = None
    width: Optional[Decimal] = None
    height: Optional[Decimal] = None
    thickness: Optional[Decimal] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class QuotationItemResponse(QuotationItemBase):
    id: int
    door_type: DoorTypeResponse
    attributes: List["QuotationItemAttributeResponse"] = []
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
    value: str
    cost_adjustment: Optional[Decimal] = Field(None, description="Cost adjustment with up to 2 decimal places")
    is_active: bool = True

    @field_validator('cost_adjustment')
    @classmethod
    def validate_decimal_places(cls, v):
        if v is not None:
            # Round to 2 decimal places
            return round(v, 2)
        return v


class QuotationItemAttributeCreate(QuotationItemAttributeBase):
    pass


class QuotationItemAttributeUpdate(QuotationItemAttributeBase):
    quotation_item_id: Optional[int] = None
    attribute_id: Optional[int] = None
    value: Optional[str] = None
    cost_adjustment: Optional[Decimal] = None
    is_active: Optional[bool] = None


class QuotationItemAttributeResponse(QuotationItemAttributeBase):
    id: int
    attribute: AttributeResponse
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
