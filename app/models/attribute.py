"""
Attribute Models
Attribute, AttributeOption, NestedAttribute, NestedAttributeChild
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.models.base import Base, CostType
from app.utils.time_utils import now_ist


class Attribute(Base):
    __tablename__ = 'attribute'
    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)
    description = Column(String)
    double_side = Column(Boolean, default=False)

    # Unified cost structure
    cost_type = Column(SAEnum(CostType, values_callable=lambda e: [member.value for member in e], name='cost_type'),
                       nullable=False)
    cost = Column(Float, nullable=True)
    unit_id = Column(Integer, ForeignKey('unit.id'))

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    options = relationship('AttributeOption', back_populates='attribute', cascade="all, delete-orphan")
    unit = relationship('Unit', back_populates='attributes')
    nested_attribute_child = relationship('NestedAttributeChild', back_populates='attribute', cascade="all, delete-orphan")
    door_type_attribute = relationship('DoorTypeAttribute', back_populates='attribute', cascade="all, delete-orphan")
    quotation_item_attribute = relationship('QuotationItemAttribute', back_populates='attribute')


class AttributeOption(Base):
    __tablename__ = 'attribute_option'

    id = Column(Integer, primary_key=True)
    attribute_id = Column(Integer, ForeignKey('attribute.id'), nullable=False)

    name = Column(String, nullable=False)
    description = Column(String)

    # Cost fields
    cost = Column(Float, nullable=True)

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    # Relationships
    attribute = relationship('Attribute', back_populates='options')
    quotation_item_attribute = relationship('QuotationItemAttribute', back_populates='selected_option')


class NestedAttribute(Base):
    __tablename__ = 'nested_attribute'

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)
    description = Column(String)

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    nested_attribute_children = relationship('NestedAttributeChild', back_populates='nested_attribute', cascade="all, delete-orphan")
    door_type_attribute = relationship('DoorTypeAttribute', back_populates='nested_attribute', cascade="all, delete-orphan")
    quotation_item_nested_attribute = relationship('QuotationItemNestedAttribute', back_populates='nested_attribute')


class NestedAttributeChild(Base):
    __tablename__ = 'nested_attribute_child'
    id = Column(Integer, primary_key=True)
    nested_attribute_id = Column(Integer, ForeignKey('nested_attribute.id'), nullable=False)
    attribute_id = Column(Integer, ForeignKey('attribute.id'), nullable=False)

    required = Column(Boolean, default=False)

    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=now_ist)
    updated_at = Column(DateTime, default=now_ist, onupdate=now_ist)

    nested_attribute = relationship('NestedAttribute', back_populates='nested_attribute_children')
    attribute = relationship('Attribute', back_populates='nested_attribute_child')
