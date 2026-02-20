"""
Service Schemas
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from enum import Enum

from app.schemas.unit import UnitResponse


class ServiceType(str, Enum):
    CONSUMABLE = 'consumable'
    ADD_ON = 'add_on'
    LABOUR = 'labour'
    GROUPING = 'grouping'


class ConsumableKind(str, Enum):
    AREA = 'area'
    LENGTH = 'length'
    WEIGHT = 'weight'
    TIME = 'time'
    PIECE = 'piece'


# ============================================================================
# SERVICE OPTION SCHEMAS
# ============================================================================

class ServiceOptionBase(BaseModel):
    service_id: int
    name: str
    description: Optional[str] = None
    cost: Optional[float] = None


class ServiceOptionCreate(ServiceOptionBase):
    service_id: Optional[int] = None


class ServiceOptionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    cost: Optional[float] = None


class ServiceOptionResponse(ServiceOptionBase):
    id: int
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# SERVICE SCHEMAS
# ============================================================================

class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    service_type: ServiceType
    consumable_kind: Optional[ConsumableKind] = None
    cost: Optional[float] = None
    both_sides: bool = False
    unit_id: Optional[int] = None


class ServiceCreate(ServiceBase):
    options: Optional[List[ServiceOptionCreate]] = None


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    service_type: Optional[ServiceType] = None
    consumable_kind: Optional[ConsumableKind] = None
    cost: Optional[float] = None
    both_sides: Optional[bool] = None
    unit_id: Optional[int] = None


class ServiceResponse(ServiceBase):
    id: int
    options: List[ServiceOptionResponse] = []
    unit: Optional[UnitResponse] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ServiceShortResponse(BaseModel):
    id: int
    name: str
    service_type: ServiceType
    consumable_kind: Optional[ConsumableKind] = None
    cost: Optional[float] = None
    both_sides: bool = False

    class Config:
        from_attributes = True


class ServiceListResponse(ServiceBase):
    id: int

    class Config:
        from_attributes = True


class PaginatedServiceResponse(BaseModel):
    data: List[ServiceResponse]
    total: int
    page: int
    size: int
    pages: int


# ============================================================================
# SERVICE GROUPING SCHEMAS
# ============================================================================

class ServiceGroupingChildBase(BaseModel):
    grouping_id: int
    service_id: int
    required: bool = False


class ServiceGroupingChildCreate(ServiceGroupingChildBase):
    grouping_id: Optional[int] = None


class ServiceGroupingChildUpdate(BaseModel):
    service_id: Optional[int] = None
    required: Optional[bool] = None


class ServiceGroupingChildResponse(ServiceGroupingChildBase):
    id: int
    service: Optional[ServiceResponse] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ServiceGroupingBase(BaseModel):
    name: str
    description: Optional[str] = None


class ServiceGroupingCreate(ServiceGroupingBase):
    children: Optional[List[ServiceGroupingChildCreate]] = None


class ServiceGroupingUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ServiceGroupingResponse(ServiceGroupingBase):
    id: int
    children: List[ServiceGroupingChildResponse] = []
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ServiceGroupingShortResponse(ServiceGroupingBase):
    id: int

    class Config:
        from_attributes = True


class PaginatedServiceGroupingResponse(BaseModel):
    data: List[ServiceGroupingResponse]
    total: int
    page: int
    size: int
    pages: int
