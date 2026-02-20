"""
Door Type Models
DoorType, DoorTypeThicknessOption, DoorTypeService
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.utils.time_utils import now_ist


class DoorType(Base):
    __tablename__ = 'door_type'

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    # Relationships
    door_type_services = relationship('DoorTypeService', back_populates='door_type', cascade="all, delete-orphan")
    items = relationship('QuotationItem', back_populates='door_type')
    thickness_options = relationship('DoorTypeThicknessOption', back_populates='door_type', cascade="all, delete-orphan")


class DoorTypeThicknessOption(Base):
    __tablename__ = 'door_type_thickness_option'

    id = Column(Integer, primary_key=True)
    door_type_id = Column(Integer, ForeignKey('door_type.id'), nullable=False)

    thickness_value = Column(Float, nullable=False)
    cost_per_sqft = Column(Float, nullable=False)

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    # Relationships
    door_type = relationship('DoorType', back_populates='thickness_options')
    quotation_items = relationship('QuotationItem', back_populates='thickness_option')


class DoorTypeService(Base):
    __tablename__ = 'door_type_service'

    id = Column(Integer, primary_key=True)

    door_type_id = Column(Integer, ForeignKey('door_type.id', ondelete='CASCADE'), nullable=False)
    service_id = Column(Integer, ForeignKey('service.id'), nullable=True)
    grouping_id = Column(Integer, ForeignKey('service_grouping.id'), nullable=True)

    required = Column(Boolean, default=False)

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    # Relationships
    service = relationship('Service', back_populates='door_type_services')
    door_type = relationship('DoorType', back_populates='door_type_services')
    grouping = relationship('ServiceGrouping', back_populates='door_type_services')

    __table_args__ = (
        UniqueConstraint('door_type_id', 'service_id', name='uq_door_type_service'),
        UniqueConstraint('door_type_id', 'grouping_id', name='uq_door_type_grouping'),
    )
