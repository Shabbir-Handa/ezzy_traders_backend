"""
Service Grouping Service
Business logic layer for ServiceGrouping and ServiceGroupingChild operations.
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import ServiceGrouping, ServiceGroupingChild
from app.repositories.service_grouping_repo import ServiceGroupingRepository
from app.schemas.service import (
    ServiceGroupingCreate, ServiceGroupingUpdate,
    ServiceGroupingChildCreate, ServiceGroupingChildUpdate,
)


class ServiceGroupingService:

    # SERVICE GROUPING
    @staticmethod
    def create_service_grouping(db: Session, data: ServiceGroupingCreate, username: str = None) -> ServiceGrouping:
        return ServiceGroupingRepository.create_service_grouping(db, data, username)

    @staticmethod
    def get_service_grouping_by_id(db: Session, grouping_id: int) -> Optional[ServiceGrouping]:
        return ServiceGroupingRepository.get_service_grouping_by_id(db, grouping_id)

    @staticmethod
    def get_all_service_groupings(db: Session, skip: int = 0, limit: int = 100) -> List[ServiceGrouping]:
        return ServiceGroupingRepository.get_all_service_groupings(db, skip, limit)

    @staticmethod
    def count_service_groupings(db: Session) -> int:
        return ServiceGroupingRepository.count_service_groupings(db)

    @staticmethod
    def update_service_grouping(db: Session, grouping_id: int, data: ServiceGroupingUpdate, username: str = None) -> Optional[ServiceGrouping]:
        return ServiceGroupingRepository.update_service_grouping(db, grouping_id, data, username)

    @staticmethod
    def delete_service_grouping(db: Session, grouping_id: int) -> bool:
        return ServiceGroupingRepository.delete_service_grouping(db, grouping_id)

    # SERVICE GROUPING CHILD
    @staticmethod
    def create_service_grouping_child(db: Session, data: ServiceGroupingChildCreate, username: str = None) -> ServiceGroupingChild:
        return ServiceGroupingRepository.create_service_grouping_child(db, data, username)

    @staticmethod
    def get_service_grouping_child_by_id(db: Session, child_id: int) -> Optional[ServiceGroupingChild]:
        return ServiceGroupingRepository.get_service_grouping_child_by_id(db, child_id)

    @staticmethod
    def update_service_grouping_child(db: Session, child_id: int, data: ServiceGroupingChildUpdate, username: str = None) -> Optional[ServiceGroupingChild]:
        return ServiceGroupingRepository.update_service_grouping_child(db, child_id, data, username)

    @staticmethod
    def delete_service_grouping_child(db: Session, child_id: int) -> bool:
        return ServiceGroupingRepository.delete_service_grouping_child(db, child_id)
