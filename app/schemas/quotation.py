"""
Quotation Schemas
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from app.schemas.customer import CustomerResponse
from app.schemas.door_type import DoorTypeShortResponse, DoorTypeThicknessOptionResponse
from app.schemas.attribute import (
    AttributeShortResponse, AttributeOptionResponse,
    NestedAttributeShortResponse
)
from app.schemas.unit import UnitResponse


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
    quotation_id: Optional[int] = None
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
    unit_price_with_attributes: Optional[float] = None
    unit_price_with_discount: Optional[float] = None
    unit_price_with_tax: Optional[float] = None
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
    quotation_item_id: Optional[int] = None
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


class PaginatedQuotationShortResponse(BaseModel):
    data: List["QuotationShortResponse"]
    total: int
    page: int
    size: int
    pages: int
