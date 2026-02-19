"""
Unit Schemas
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


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


class PaginatedUnitResponse(BaseModel):
    data: List["UnitResponse"]
    total: int
    page: int
    size: int
    pages: int
