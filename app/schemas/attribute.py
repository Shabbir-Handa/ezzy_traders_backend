"""
Attribute Schemas
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from enum import Enum

from app.schemas.unit import UnitResponse


class CostType(str, Enum):
    """Cost type enumeration for attributes"""
    CONSTANT = 'constant'
    VARIABLE = 'variable'
    DIRECT = 'direct'


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
    nested_attribute_children: List["NestedAttributeChildResponse"] = []
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
