"""
Service Grouping Repository
Data access layer for ServiceGrouping and ServiceGroupingChild entities.
"""

from sqlalchemy.orm import Session, selectinload
from typing import List, Optional

from app.models import Service, ServiceGrouping, ServiceGroupingChild
from app.schemas.service import (
    ServiceGroupingCreate, ServiceGroupingUpdate,
    ServiceGroupingChildCreate, ServiceGroupingChildUpdate,
)


class ServiceGroupingRepository:

    # ========================================================================
    # SERVICE GROUPING
    # ========================================================================

    @staticmethod
    def create_service_grouping(db: Session, data: ServiceGroupingCreate, username: str = None) -> ServiceGrouping:
        grouping = ServiceGrouping(
            name=data.name,
            description=data.description,
            created_by=username or "system",
            updated_by=username or "system",
        )
        db.add(grouping)
        db.flush()

        if data.children:
            for child_data in data.children:
                child = ServiceGroupingChild(
                    grouping_id=grouping.id,
                    service_id=child_data.service_id,
                    required=child_data.required,
                    created_by=username or "system",
                    updated_by=username or "system",
                )
                db.add(child)

        db.commit()
        db.refresh(grouping)
        return grouping

    @staticmethod
    def get_service_grouping_by_id(db: Session, grouping_id: int) -> Optional[ServiceGrouping]:
        return db.query(ServiceGrouping).options(
            selectinload(ServiceGrouping.children).selectinload(ServiceGroupingChild.service).selectinload(Service.options),
            selectinload(ServiceGrouping.children).selectinload(ServiceGroupingChild.service).selectinload(Service.unit),
        ).filter(ServiceGrouping.id == grouping_id).first()

    @staticmethod
    def get_all_service_groupings(db: Session, skip: int = 0, limit: int = 100) -> List[ServiceGrouping]:
        return db.query(ServiceGrouping).options(
            selectinload(ServiceGrouping.children).selectinload(ServiceGroupingChild.service).selectinload(Service.options),
            selectinload(ServiceGrouping.children).selectinload(ServiceGroupingChild.service).selectinload(Service.unit),
        ).offset(skip).limit(limit).all()

    @staticmethod
    def count_service_groupings(db: Session) -> int:
        return db.query(ServiceGrouping).count()

    @staticmethod
    def update_service_grouping(db: Session, grouping_id: int, data: ServiceGroupingUpdate, username: str = None) -> Optional[ServiceGrouping]:
        grouping = db.query(ServiceGrouping).filter(ServiceGrouping.id == grouping_id).first()
        if not grouping:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(grouping, key, value)
        if username:
            grouping.updated_by = username
        db.commit()
        db.refresh(grouping)
        return grouping

    @staticmethod
    def delete_service_grouping(db: Session, grouping_id: int) -> bool:
        grouping = db.query(ServiceGrouping).filter(ServiceGrouping.id == grouping_id).first()
        if not grouping:
            return False
        db.delete(grouping)
        db.commit()
        return True

    # ========================================================================
    # SERVICE GROUPING CHILD
    # ========================================================================

    @staticmethod
    def create_service_grouping_child(db: Session, data: ServiceGroupingChildCreate, username: str = None) -> ServiceGroupingChild:
        child = ServiceGroupingChild(
            grouping_id=data.grouping_id,
            service_id=data.service_id,
            required=data.required,
            created_by=username or "system",
            updated_by=username or "system",
        )
        db.add(child)
        db.commit()
        db.refresh(child)
        return child

    @staticmethod
    def get_service_grouping_child_by_id(db: Session, child_id: int) -> Optional[ServiceGroupingChild]:
        return db.query(ServiceGroupingChild).options(
            selectinload(ServiceGroupingChild.service).selectinload(Service.options),
        ).filter(ServiceGroupingChild.id == child_id).first()

    @staticmethod
    def update_service_grouping_child(db: Session, child_id: int, data: ServiceGroupingChildUpdate, username: str = None) -> Optional[ServiceGroupingChild]:
        child = db.query(ServiceGroupingChild).filter(ServiceGroupingChild.id == child_id).first()
        if not child:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(child, key, value)
        if username:
            child.updated_by = username
        db.commit()
        db.refresh(child)
        return child

    @staticmethod
    def delete_service_grouping_child(db: Session, child_id: int) -> bool:
        child = db.query(ServiceGroupingChild).filter(ServiceGroupingChild.id == child_id).first()
        if not child:
            return False
        db.delete(child)
        db.commit()
        return True
