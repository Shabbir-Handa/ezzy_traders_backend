"""
Unit Repository
Data access layer for Unit entities.
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import Unit
from app.schemas.unit import UnitCreate, UnitUpdate


class UnitRepository:

    @staticmethod
    def create_unit(db: Session, data: UnitCreate, username: str = None) -> Unit:
        unit = Unit(
            name=data.name,
            abbreviation=data.abbreviation,
            unit_type=data.unit_type,
            created_by=username or "system",
            updated_by=username or "system",
        )
        db.add(unit)
        db.commit()
        db.refresh(unit)
        return unit

    @staticmethod
    def get_unit_by_id(db: Session, unit_id: int) -> Optional[Unit]:
        return db.query(Unit).filter(Unit.id == unit_id).first()

    @staticmethod
    def get_all_units(db: Session, skip: int = 0, limit: int = 100) -> List[Unit]:
        return db.query(Unit).offset(skip).limit(limit).all()

    @staticmethod
    def count_units(db: Session) -> int:
        return db.query(Unit).count()

    @staticmethod
    def update_unit(db: Session, unit_id: int, data: UnitUpdate, username: str = None) -> Optional[Unit]:
        unit = db.query(Unit).filter(Unit.id == unit_id).first()
        if not unit:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(unit, key, value)
        if username:
            unit.updated_by = username
        db.commit()
        db.refresh(unit)
        return unit

    @staticmethod
    def delete_unit(db: Session, unit_id: int) -> bool:
        unit = db.query(Unit).filter(Unit.id == unit_id).first()
        if not unit:
            return False
        db.delete(unit)
        db.commit()
        return True
