"""
Common Response Schemas
"""

from typing import List
from pydantic import BaseModel


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
