"""
Door Type Models
DoorType, DoorTypeThicknessOption, DoorTypeAttribute
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.utils.time_utils import now_ist


class DoorType(Base):
    __tablename__ = 'door_type'

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)
    description = Column(String)

    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    # Many-to-many with Attribute via DoorTypeAttribute
    door_type_attributes = relationship('DoorTypeAttribute', back_populates='door_type', cascade="all, delete-orphan")
    # One-to-many to quotation items
    items = relationship('QuotationItem', back_populates='door_type')
    # One-to-many to thickness options
    thickness_options = relationship('DoorTypeThicknessOption', back_populates='door_type')


class DoorTypeThicknessOption(Base):
    __tablename__ = 'door_type_thickness_option'

    id = Column(Integer, primary_key=True)
    door_type_id = Column(Integer, ForeignKey('door_type.id'), nullable=False)

    thickness_value = Column(Float, nullable=False)
    cost_per_sqft = Column(Float, nullable=False)

    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    door_type = relationship('DoorType', back_populates='thickness_options')
    quotation_items = relationship('QuotationItem', back_populates='thickness_option')


class DoorTypeAttribute(Base):
    __tablename__ = 'door_type_attribute'
    id = Column(Integer, primary_key=True)

    door_type_id = Column(Integer, ForeignKey('door_type.id', ondelete='CASCADE'), nullable=False)
    attribute_id = Column(Integer, ForeignKey('attribute.id'), nullable=True)
    nested_attribute_id = Column(Integer, ForeignKey('nested_attribute.id'), nullable=True)

    # Common fields
    required = Column(Boolean, default=False)

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    # Relationships
    attribute = relationship('Attribute', back_populates='door_type_attribute')
    door_type = relationship('DoorType', back_populates='door_type_attributes')
    nested_attribute = relationship('NestedAttribute', back_populates='door_type_attribute')

    __table_args__ = (
        UniqueConstraint('door_type_id', 'attribute_id', name='uq_door_type_attribute'),
        UniqueConstraint('door_type_id', 'nested_attribute_id', name='uq_door_type_nested_attribute')
    )
