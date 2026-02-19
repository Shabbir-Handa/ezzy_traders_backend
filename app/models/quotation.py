"""
Quotation Models
Quotation, QuotationItem, QuotationItemAttribute, QuotationItemNestedAttribute, UnitValue
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, Date
from sqlalchemy.orm import relationship
from datetime import date
from app.models.base import Base
from app.utils.time_utils import now_ist


class Quotation(Base):
    __tablename__ = 'quotation'

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customer_details.id'), nullable=False)

    date = Column(Date, nullable=False, default=date.today())
    status = Column(String, default='pending')
    quotation_number = Column(String, nullable=False, unique=True)
    total_amount = Column(Float, nullable=False, default=0)

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    customer = relationship('Customer', back_populates='quotations')
    items = relationship('QuotationItem', back_populates='quotation', cascade="all, delete-orphan")


class QuotationItem(Base):
    __tablename__ = 'quotation_item'

    id = Column(Integer, primary_key=True)
    quotation_id = Column(Integer, ForeignKey('quotation.id'), nullable=False)
    door_type_id = Column(Integer, ForeignKey('door_type.id'), nullable=False)
    thickness_option_id = Column(Integer, ForeignKey('door_type_thickness_option.id'), nullable=False)

    length = Column(Float, nullable=False)
    breadth = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    # Cost breakdown fields
    base_cost_per_unit = Column(Float, nullable=False, default=0)
    attribute_cost_per_unit = Column(Float, nullable=False, default=0)
    unit_price_with_attributes = Column(Float, nullable=False, default=0)
    unit_price_with_discount = Column(Float, nullable=False, default=0)
    unit_price_with_tax = Column(Float, nullable=False, default=0)
    total_item_cost = Column(Float, nullable=False, default=0)

    # Tax and discount
    tax_percentage = Column(Float, nullable=False, default=0)
    discount_amount = Column(Float, nullable=False, default=0)

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    quotation = relationship('Quotation', back_populates='items')
    door_type = relationship('DoorType', back_populates='items')
    thickness_option = relationship('DoorTypeThicknessOption', back_populates='quotation_items')
    attributes = relationship('QuotationItemAttribute', back_populates='quotation_item', cascade="all, delete-orphan")


class QuotationItemAttribute(Base):
    __tablename__ = 'quotation_item_attribute'
    id = Column(Integer, primary_key=True)
    quotation_item_id = Column(Integer, ForeignKey('quotation_item.id'), nullable=False)
    quotation_item_nested_attribute_id = Column(Integer, ForeignKey('quotation_item_nested_attribute.id'), nullable=True)
    attribute_id = Column(Integer, ForeignKey('attribute.id'), nullable=False)
    selected_option_id = Column(Integer, ForeignKey('attribute_option.id'), nullable=True)

    double_side = Column(Boolean, default=False)
    direct_cost = Column(Float, nullable=True)
    calculated_cost = Column(Float, nullable=True)
    total_attribute_cost = Column(Float, nullable=False, default=0)

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    quotation_item = relationship('QuotationItem', back_populates='attributes')
    quotation_item_nested_attribute = relationship('QuotationItemNestedAttribute', back_populates='quotation_item_attribute')
    attribute = relationship('Attribute', back_populates='quotation_item_attribute')
    selected_option = relationship('AttributeOption', back_populates='quotation_item_attribute')
    unit_values = relationship('UnitValue', back_populates='quotation_item_attribute', cascade="all, delete-orphan")


class QuotationItemNestedAttribute(Base):
    __tablename__ = 'quotation_item_nested_attribute'
    id = Column(Integer, primary_key=True)
    nested_attribute_id = Column(Integer, ForeignKey('nested_attribute.id'), nullable=False)

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    nested_attribute = relationship('NestedAttribute', back_populates='quotation_item_nested_attribute')
    quotation_item_attribute = relationship('QuotationItemAttribute', back_populates='quotation_item_nested_attribute', cascade="all, delete-orphan")


class UnitValue(Base):
    __tablename__ = 'unit_value'

    id = Column(Integer, primary_key=True)
    quotation_item_attribute_id = Column(Integer, ForeignKey('quotation_item_attribute.id'), nullable=False)
    unit_id = Column(Integer, ForeignKey('unit.id'), nullable=False)

    value1 = Column(Float, nullable=True)
    value2 = Column(Float, nullable=True)

    unit = relationship('Unit', back_populates='unit_values')
    quotation_item_attribute = relationship('QuotationItemAttribute', back_populates='unit_values')
