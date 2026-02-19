"""
Base Model & Shared Enums
"""

from sqlalchemy.ext.declarative import declarative_base
from enum import Enum as PyEnum

Base = declarative_base()


class CostType(PyEnum):
    CONSTANT = 'constant'
    VARIABLE = 'variable'
    DIRECT = 'direct'
