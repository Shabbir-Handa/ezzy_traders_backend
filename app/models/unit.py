"""
Unit Model
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.utils.time_utils import now_ist


class Unit(Base):
    __tablename__ = 'unit'

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)
    abbreviation = Column(String, nullable=True)
    unit_type = Column(String(20), nullable=False)

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    # Relationships
    services = relationship('Service', back_populates='unit')
    unit_values = relationship('QuotationItemServiceUnitValue', back_populates='unit')
