"""
Unit Service
Business logic layer for Unit operations.
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import Unit
from app.repositories.unit_repo import UnitRepository
from app.schemas.unit import UnitCreate, UnitUpdate


class UnitService:

    @staticmethod
    def create_unit(db: Session, data: UnitCreate, username: str = None) -> Unit:
        return UnitRepository.create_unit(db, data, username)

    @staticmethod
    def get_unit_by_id(db: Session, unit_id: int) -> Optional[Unit]:
        return UnitRepository.get_unit_by_id(db, unit_id)

    @staticmethod
    def get_all_units(db: Session, skip: int = 0, limit: int = 100) -> List[Unit]:
        return UnitRepository.get_all_units(db, skip, limit)

    @staticmethod
    def count_units(db: Session) -> int:
        return UnitRepository.count_units(db)

    @staticmethod
    def update_unit(db: Session, unit_id: int, data: UnitUpdate, username: str = None) -> Optional[Unit]:
        return UnitRepository.update_unit(db, unit_id, data, username)

    @staticmethod
    def delete_unit(db: Session, unit_id: int) -> bool:
        return UnitRepository.delete_unit(db, unit_id)
