"""
Quotation Models
Quotation, QuotationItem, QuotationItemService, QuotationItemServiceUnitValue
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, Date, Text
from sqlalchemy.orm import relationship
from datetime import date
from app.models.base import Base
from app.utils.time_utils import now_ist


class Quotation(Base):
    __tablename__ = 'quotation'

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customer_details.id'), nullable=False)

    date = Column(Date, nullable=False, default=date.today)
    status = Column(String, default='draft')
    quotation_number = Column(String, nullable=False, unique=True)
    total = Column(Float, nullable=False, default=0)
    notes = Column(Text, nullable=True)

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    # Relationships
    customer = relationship('Customer', back_populates='quotations')
    items = relationship('QuotationItem', back_populates='quotation', cascade="all, delete-orphan")


class QuotationItem(Base):
    __tablename__ = 'quotation_item'

    id = Column(Integer, primary_key=True)
    quotation_id = Column(Integer, ForeignKey('quotation.id'), nullable=False)
    door_type_id = Column(Integer, ForeignKey('door_type.id'), nullable=False)
    thickness_option_id = Column(Integer, ForeignKey('door_type_thickness_option.id'), nullable=False)

    # User inputs
    length = Column(Float, nullable=False)
    breadth = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    tax_percent = Column(Float, nullable=False, default=0)
    discount = Column(Float, nullable=False, default=0)

    # Cost breakdown (single linear flow)
    base_cost = Column(Float, nullable=False, default=0)
    services_cost = Column(Float, nullable=False, default=0)
    subtotal = Column(Float, nullable=False, default=0)
    total_after_discount = Column(Float, nullable=False, default=0)
    tax_amount = Column(Float, nullable=False, default=0)
    total = Column(Float, nullable=False, default=0)

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    # Relationships
    quotation = relationship('Quotation', back_populates='items')
    door_type = relationship('DoorType', back_populates='items')
    thickness_option = relationship('DoorTypeThicknessOption', back_populates='quotation_items')
    services = relationship('QuotationItemService', back_populates='quotation_item', cascade="all, delete-orphan")


class QuotationItemService(Base):
    __tablename__ = 'quotation_item_service'

    id = Column(Integer, primary_key=True)
    quotation_item_id = Column(Integer, ForeignKey('quotation_item.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('service.id'), nullable=False)
    parent_id = Column(Integer, ForeignKey('quotation_item_service.id'), nullable=True)
    option_id = Column(Integer, ForeignKey('service_option.id'), nullable=True)

    quantity = Column(Float, nullable=True)
    direct_amount = Column(Float, nullable=True)
    both_sides = Column(Boolean, default=False)
    cost = Column(Float, nullable=False, default=0)

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    # Relationships
    quotation_item = relationship('QuotationItem', back_populates='services')
    service = relationship('Service', back_populates='quotation_item_services')
    selected_option = relationship('ServiceOption', back_populates='quotation_item_services')
    parent = relationship('QuotationItemService', remote_side=[id], backref='children')
    unit_values = relationship('QuotationItemServiceUnitValue', back_populates='quotation_item_service', cascade="all, delete-orphan")


class QuotationItemServiceUnitValue(Base):
    __tablename__ = 'quotation_item_service_unit_value'

    id = Column(Integer, primary_key=True)
    quotation_item_service_id = Column(Integer, ForeignKey('quotation_item_service.id'), nullable=False)
    unit_id = Column(Integer, ForeignKey('unit.id'), nullable=False)

    value1 = Column(Float, nullable=True)
    value2 = Column(Float, nullable=True)

    # Relationships
    unit = relationship('Unit', back_populates='unit_values')
    quotation_item_service = relationship('QuotationItemService', back_populates='unit_values')
