"""
Service Service
Business logic layer for Service and ServiceOption operations.
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import Service as ServiceModel, ServiceOption
from app.repositories.service_repo import ServiceRepository
from app.schemas.service import (
    ServiceCreate, ServiceUpdate,
    ServiceOptionCreate, ServiceOptionUpdate,
)


class ServiceService:

    # SERVICE
    @staticmethod
    def create_service(db: Session, data: ServiceCreate, username: str = None) -> ServiceModel:
        return ServiceRepository.create_service(db, data, username)

    @staticmethod
    def get_service_by_id(db: Session, service_id: int) -> Optional[ServiceModel]:
        return ServiceRepository.get_service_by_id(db, service_id)

    @staticmethod
    def get_all_services(db: Session, skip: int = 0, limit: int = 100) -> List[ServiceModel]:
        return ServiceRepository.get_all_services(db, skip, limit)

    @staticmethod
    def count_services(db: Session) -> int:
        return ServiceRepository.count_services(db)

    @staticmethod
    def update_service(db: Session, service_id: int, data: ServiceUpdate, username: str = None) -> Optional[ServiceModel]:
        return ServiceRepository.update_service(db, service_id, data, username)

    @staticmethod
    def delete_service(db: Session, service_id: int) -> bool:
        return ServiceRepository.delete_service(db, service_id)

    # SERVICE OPTION
    @staticmethod
    def create_service_option(db: Session, data: ServiceOptionCreate, username: str = None) -> ServiceOption:
        return ServiceRepository.create_service_option(db, data, username)

    @staticmethod
    def get_service_options_by_service(db: Session, service_id: int) -> List[ServiceOption]:
        return ServiceRepository.get_service_options_by_service(db, service_id)

    @staticmethod
    def get_service_option_by_id(db: Session, option_id: int) -> Optional[ServiceOption]:
        return ServiceRepository.get_service_option_by_id(db, option_id)

    @staticmethod
    def update_service_option(db: Session, option_id: int, data: ServiceOptionUpdate, username: str = None) -> Optional[ServiceOption]:
        return ServiceRepository.update_service_option(db, option_id, data, username)

    @staticmethod
    def delete_service_option(db: Session, option_id: int) -> bool:
        return ServiceRepository.delete_service_option(db, option_id)
