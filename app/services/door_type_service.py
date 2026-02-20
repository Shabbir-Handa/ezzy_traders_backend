"""
Door Type Service
Business logic layer for DoorType, ThicknessOption, and DoorTypeService operations.
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import DoorType, DoorTypeThicknessOption, DoorTypeService
from app.repositories.door_type_repo import DoorTypeRepository
from app.schemas.door_type import (
    DoorTypeCreate, DoorTypeUpdate,
    DoorTypeThicknessOptionCreate, DoorTypeThicknessOptionUpdate,
    DoorTypeServiceCreate, DoorTypeServiceUpdate,
)


class DoorTypeService:

    # DOOR TYPE
    @staticmethod
    def create_door_type(db: Session, data: DoorTypeCreate, username: str = None) -> DoorType:
        return DoorTypeRepository.create_door_type(db, data, username)

    @staticmethod
    def get_door_type_by_id(db: Session, door_type_id: int) -> Optional[DoorType]:
        return DoorTypeRepository.get_door_type_by_id(db, door_type_id)

    @staticmethod
    def get_all_door_types(db: Session, skip: int = 0, limit: int = 100) -> List[DoorType]:
        return DoorTypeRepository.get_all_door_types(db, skip, limit)

    @staticmethod
    def count_door_types(db: Session) -> int:
        return DoorTypeRepository.count_door_types(db)

    @staticmethod
    def update_door_type(db: Session, door_type_id: int, data: DoorTypeUpdate, username: str = None) -> Optional[DoorType]:
        return DoorTypeRepository.update_door_type(db, door_type_id, data, username)

    @staticmethod
    def delete_door_type(db: Session, door_type_id: int) -> bool:
        return DoorTypeRepository.delete_door_type(db, door_type_id)

    # THICKNESS OPTION
    @staticmethod
    def create_door_type_thickness_option(db: Session, data: DoorTypeThicknessOptionCreate, username: str = None) -> DoorTypeThicknessOption:
        return DoorTypeRepository.create_door_type_thickness_option(db, data, username)

    @staticmethod
    def get_door_type_thickness_option_by_id(db: Session, option_id: int) -> Optional[DoorTypeThicknessOption]:
        return DoorTypeRepository.get_door_type_thickness_option_by_id(db, option_id)

    @staticmethod
    def get_door_type_thickness_options_by_door_type(db: Session, door_type_id: int) -> List[DoorTypeThicknessOption]:
        return DoorTypeRepository.get_door_type_thickness_options_by_door_type(db, door_type_id)

    @staticmethod
    def update_door_type_thickness_option(db: Session, option_id: int, data: DoorTypeThicknessOptionUpdate, username: str = None) -> Optional[DoorTypeThicknessOption]:
        return DoorTypeRepository.update_door_type_thickness_option(db, option_id, data, username)

    @staticmethod
    def delete_door_type_thickness_option(db: Session, option_id: int) -> bool:
        return DoorTypeRepository.delete_door_type_thickness_option(db, option_id)

    # DOOR TYPE SERVICE
    @staticmethod
    def create_door_type_service_link(db: Session, data: DoorTypeServiceCreate, username: str = None):
        return DoorTypeRepository.create_door_type_service(db, data, username)

    @staticmethod
    def get_door_type_services_by_door_type(db: Session, door_type_id: int):
        return DoorTypeRepository.get_door_type_services_by_door_type(db, door_type_id)

    @staticmethod
    def get_door_type_service_by_id(db: Session, dts_id: int):
        return DoorTypeRepository.get_door_type_service_by_id(db, dts_id)

    @staticmethod
    def update_door_type_service(db: Session, dts_id: int, data: DoorTypeServiceUpdate, username: str = None):
        return DoorTypeRepository.update_door_type_service(db, dts_id, data, username)

    @staticmethod
    def delete_door_type_service(db: Session, dts_id: int) -> bool:
        return DoorTypeRepository.delete_door_type_service(db, dts_id)
