"""
Employee Schemas
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


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


class PaginatedEmployeeResponse(BaseModel):
    data: list["EmployeeResponse"]
    total: int
    page: int
    size: int
    pages: int
