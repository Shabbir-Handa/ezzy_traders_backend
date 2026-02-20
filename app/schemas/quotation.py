"""
Quotation Schemas
"""

from datetime import datetime, date as date_type
from typing import Optional, List
from pydantic import BaseModel

from app.schemas.customer import CustomerResponse
from app.schemas.door_type import DoorTypeShortResponse, DoorTypeThicknessOptionResponse
from app.schemas.service import ServiceShortResponse, ServiceOptionResponse
from app.schemas.unit import UnitResponse


# ============================================================================
# QUOTATION ITEM SERVICE UNIT VALUE SCHEMAS
# ============================================================================

class QuotationItemServiceUnitValueBase(BaseModel):
    quotation_item_service_id: int
    unit_id: int
    value1: Optional[float] = None
    value2: Optional[float] = None


class QuotationItemServiceUnitValueCreate(QuotationItemServiceUnitValueBase):
    quotation_item_service_id: Optional[int] = None


class QuotationItemServiceUnitValueResponse(QuotationItemServiceUnitValueBase):
    id: int
    unit: Optional[UnitResponse] = None

    class Config:
        from_attributes = True


# ============================================================================
# QUOTATION ITEM SERVICE SCHEMAS
# ============================================================================

class QuotationItemServiceBase(BaseModel):
    quotation_item_id: int
    service_id: int
    parent_id: Optional[int] = None
    option_id: Optional[int] = None
    quantity: Optional[float] = None
    direct_amount: Optional[float] = None
    both_sides: bool = False


class QuotationItemServiceCreate(QuotationItemServiceBase):
    quotation_item_id: Optional[int] = None
    unit_values: Optional[List[QuotationItemServiceUnitValueCreate]] = None


class QuotationItemServiceUpdate(BaseModel):
    service_id: Optional[int] = None
    parent_id: Optional[int] = None
    option_id: Optional[int] = None
    quantity: Optional[float] = None
    direct_amount: Optional[float] = None
    both_sides: Optional[bool] = None


class QuotationItemServiceResponse(QuotationItemServiceBase):
    id: int
    service: Optional[ServiceShortResponse] = None
    selected_option: Optional[ServiceOptionResponse] = None
    unit_values: List[QuotationItemServiceUnitValueResponse] = []
    cost: float = 0
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# QUOTATION ITEM SCHEMAS
# ============================================================================

class QuotationItemBase(BaseModel):
    quotation_id: int
    door_type_id: int
    thickness_option_id: int
    length: float
    breadth: float
    quantity: int = 1
    tax_percent: float = 0
    discount: float = 0


class QuotationItemCreate(QuotationItemBase):
    quotation_id: Optional[int] = None
    services: Optional[List[QuotationItemServiceCreate]] = None


class QuotationItemUpdate(BaseModel):
    door_type_id: Optional[int] = None
    thickness_option_id: Optional[int] = None
    length: Optional[float] = None
    breadth: Optional[float] = None
    quantity: Optional[int] = None
    tax_percent: Optional[float] = None
    discount: Optional[float] = None


class QuotationItemResponse(BaseModel):
    id: int
    quotation_id: int
    door_type_id: int
    thickness_option_id: int
    length: float
    breadth: float
    quantity: int
    tax_percent: float
    discount: float

    # Cost breakdown
    base_cost: float = 0
    services_cost: float = 0
    subtotal: float = 0
    total_after_discount: float = 0
    tax_amount: float = 0
    total: float = 0

    # Related data
    door_type: Optional[DoorTypeShortResponse] = None
    thickness_option: Optional[DoorTypeThicknessOptionResponse] = None
    services: List[QuotationItemServiceResponse] = []

    # Audit fields
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# QUOTATION SCHEMAS
# ============================================================================

class QuotationBase(BaseModel):
    customer_id: int
    date: Optional[date_type] = None
    status: str = 'draft'
    notes: Optional[str] = None


class QuotationCreate(QuotationBase):
    items: Optional[List[QuotationItemCreate]] = None


class QuotationUpdate(BaseModel):
    customer_id: Optional[int] = None
    date: Optional[date_type] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class QuotationResponse(BaseModel):
    id: int
    customer_id: int
    date: Optional[date_type] = None
    status: str
    quotation_number: str
    total: float = 0
    notes: Optional[str] = None
    customer: Optional[CustomerResponse] = None
    items: List[QuotationItemResponse] = []
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class QuotationShortResponse(BaseModel):
    id: int
    customer_id: int
    date: Optional[date_type] = None
    status: str
    quotation_number: str
    total: float = 0
    customer: Optional[CustomerResponse] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaginatedQuotationShortResponse(BaseModel):
    data: List[QuotationShortResponse]
    total: int
    page: int
    size: int
    pages: int
