"""
Service Models
Service, ServiceOption, ServiceGrouping, ServiceGroupingChild
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.models.base import Base, ServiceType, ConsumableKind
from app.utils.time_utils import now_ist


class Service(Base):
    __tablename__ = 'service'

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    service_type = Column(
        SAEnum(ServiceType, values_callable=lambda e: [m.value for m in e], name='service_type'),
        nullable=False
    )
    consumable_kind = Column(
        SAEnum(ConsumableKind, values_callable=lambda e: [m.value for m in e], name='consumable_kind'),
        nullable=True
    )
    cost = Column(Float, nullable=True)
    both_sides = Column(Boolean, default=False)
    unit_id = Column(Integer, ForeignKey('unit.id'), nullable=True)

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    # Relationships
    options = relationship('ServiceOption', back_populates='service', cascade="all, delete-orphan")
    unit = relationship('Unit', back_populates='services')
    grouping_children = relationship('ServiceGroupingChild', back_populates='service')
    door_type_services = relationship('DoorTypeService', back_populates='service')
    quotation_item_services = relationship('QuotationItemService', back_populates='service')


class ServiceOption(Base):
    __tablename__ = 'service_option'

    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey('service.id'), nullable=False)

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    cost = Column(Float, nullable=True)

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    # Relationships
    service = relationship('Service', back_populates='options')
    quotation_item_services = relationship('QuotationItemService', back_populates='selected_option')


class ServiceGrouping(Base):
    __tablename__ = 'service_grouping'

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    # Relationships
    children = relationship('ServiceGroupingChild', back_populates='grouping', cascade="all, delete-orphan")
    door_type_services = relationship('DoorTypeService', back_populates='grouping')


class ServiceGroupingChild(Base):
    __tablename__ = 'service_grouping_child'

    id = Column(Integer, primary_key=True)
    grouping_id = Column(Integer, ForeignKey('service_grouping.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('service.id'), nullable=False)

    required = Column(Boolean, default=False)

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    # Relationships
    grouping = relationship('ServiceGrouping', back_populates='children')
    service = relationship('Service', back_populates='grouping_children')
