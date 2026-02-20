"""
Door Type Schemas
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class DoorTypeBase(BaseModel):
    name: str
    description: Optional[str] = None


class DoorTypeCreate(DoorTypeBase):
    thickness_options: Optional[List["DoorTypeThicknessOptionCreate"]] = None


class DoorTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class DoorTypeResponse(DoorTypeBase):
    id: int
    door_type_services: Optional[List["DoorTypeServiceResponse"]] = None
    thickness_options: Optional[List["DoorTypeThicknessOptionResponse"]] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DoorTypeShortResponse(DoorTypeBase):
    id: int

    class Config:
        from_attributes = True


# ============================================================================
# DOOR TYPE THICKNESS OPTION SCHEMAS
# ============================================================================

class DoorTypeThicknessOptionBase(BaseModel):
    door_type_id: int
    thickness_value: float
    cost_per_sqft: float


class DoorTypeThicknessOptionCreate(DoorTypeThicknessOptionBase):
    door_type_id: Optional[int] = None


class DoorTypeThicknessOptionUpdate(BaseModel):
    thickness_value: Optional[float] = None
    cost_per_sqft: Optional[float] = None


class DoorTypeThicknessOptionResponse(DoorTypeThicknessOptionBase):
    id: int
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# DOOR TYPE SERVICE SCHEMAS
# ============================================================================

class DoorTypeServiceBase(BaseModel):
    door_type_id: int
    service_id: Optional[int] = None
    grouping_id: Optional[int] = None
    required: bool = False


class DoorTypeServiceCreate(DoorTypeServiceBase):
    pass


class DoorTypeServiceUpdate(BaseModel):
    service_id: Optional[int] = None
    grouping_id: Optional[int] = None
    required: Optional[bool] = None


class DoorTypeServiceResponse(DoorTypeServiceBase):
    id: int
    service: Optional["ServiceResponse"] = None
    grouping: Optional["ServiceGroupingShortResponse"] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaginatedDoorTypeResponse(BaseModel):
    data: List[DoorTypeResponse]
    total: int
    page: int
    size: int
    pages: int


# Forward reference imports for type resolution
from app.schemas.service import ServiceResponse, ServiceGroupingShortResponse  # noqa: E402, F811

DoorTypeServiceResponse.model_rebuild()
DoorTypeResponse.model_rebuild()
