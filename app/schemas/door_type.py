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


class DoorTypeUpdate(DoorTypeBase):
    name: Optional[str] = None
    description: Optional[str] = None


class DoorTypeResponse(DoorTypeBase):
    id: int
    door_type_attributes: Optional[List["DoorTypeAttributeResponse"]] = None
    thickness_options: Optional[List["DoorTypeThicknessOptionResponse"]] = None
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


class PaginatedDoorTypeResponse(BaseModel):
    data: List["DoorTypeResponse"]
    total: int
    page: int
    size: int
    pages: int


# Forward reference imports for type resolution
from app.schemas.attribute import AttributeResponse, NestedAttributeResponse  # noqa: E402, F811

DoorTypeAttributeResponse.model_rebuild()
DoorTypeResponse.model_rebuild()
