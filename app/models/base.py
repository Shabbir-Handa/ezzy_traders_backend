"""
Base Model & Shared Enums
"""

from sqlalchemy.orm import declarative_base
from enum import Enum as PyEnum

Base = declarative_base()


class ServiceType(PyEnum):
    CONSUMABLE = 'consumable'
    ADD_ON = 'add_on'
    LABOUR = 'labour'
    GROUPING = 'grouping'


class ConsumableKind(PyEnum):
    AREA = 'area'
    LENGTH = 'length'
    WEIGHT = 'weight'
    TIME = 'time'
    PIECE = 'piece'
