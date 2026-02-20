"""
Door Service Service
Business logic layer for DoorType, Service, ServiceGrouping, and Unit operations.
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import (
    DoorType, DoorTypeThicknessOption, DoorTypeService,
    Service, ServiceOption, ServiceGrouping, ServiceGroupingChild,
    Unit,
)
from app.repositories.door_service_repo import DoorServiceRepository
from app.schemas.door_type import (
    DoorTypeCreate, DoorTypeUpdate,
    DoorTypeThicknessOptionCreate, DoorTypeThicknessOptionUpdate,
    DoorTypeServiceCreate, DoorTypeServiceUpdate,
)
from app.schemas.service import (
    ServiceCreate, ServiceUpdate,
    ServiceOptionCreate, ServiceOptionUpdate,
    ServiceGroupingCreate, ServiceGroupingUpdate,
    ServiceGroupingChildCreate, ServiceGroupingChildUpdate,
)
from app.schemas.unit import UnitCreate, UnitUpdate


class DoorServiceService:

    # ========================================================================
    # DOOR TYPE
    # ========================================================================

    @staticmethod
    def create_door_type(db: Session, data: DoorTypeCreate, username: str = None) -> DoorType:
        return DoorServiceRepository.create_door_type(db, data, username)

    @staticmethod
    def get_door_type_by_id(db: Session, door_type_id: int) -> Optional[DoorType]:
        return DoorServiceRepository.get_door_type_by_id(db, door_type_id)

    @staticmethod
    def get_all_door_types(db: Session, skip: int = 0, limit: int = 100) -> List[DoorType]:
        return DoorServiceRepository.get_all_door_types(db, skip, limit)

    @staticmethod
    def count_door_types(db: Session) -> int:
        return DoorServiceRepository.count_door_types(db)

    @staticmethod
    def update_door_type(db: Session, door_type_id: int, data: DoorTypeUpdate, username: str = None) -> Optional[DoorType]:
        return DoorServiceRepository.update_door_type(db, door_type_id, data, username)

    @staticmethod
    def delete_door_type(db: Session, door_type_id: int) -> bool:
        return DoorServiceRepository.delete_door_type(db, door_type_id)

    # ========================================================================
    # THICKNESS OPTIONS
    # ========================================================================

    @staticmethod
    def create_door_type_thickness_option(db: Session, data: DoorTypeThicknessOptionCreate, username: str = None):
        return DoorServiceRepository.create_door_type_thickness_option(db, data, username)

    @staticmethod
    def get_door_type_thickness_option_by_id(db: Session, option_id: int):
        return DoorServiceRepository.get_door_type_thickness_option_by_id(db, option_id)

    @staticmethod
    def get_door_type_thickness_options_by_door_type(db: Session, door_type_id: int):
        return DoorServiceRepository.get_door_type_thickness_options_by_door_type(db, door_type_id)

    @staticmethod
    def update_door_type_thickness_option(db: Session, option_id: int, data: DoorTypeThicknessOptionUpdate, username: str = None):
        return DoorServiceRepository.update_door_type_thickness_option(db, option_id, data, username)

    @staticmethod
    def delete_door_type_thickness_option(db: Session, option_id: int):
        return DoorServiceRepository.delete_door_type_thickness_option(db, option_id)

    # ========================================================================
    # SERVICE
    # ========================================================================

    @staticmethod
    def create_service(db: Session, data: ServiceCreate, username: str = None) -> Service:
        return DoorServiceRepository.create_service(db, data, username)

    @staticmethod
    def get_service_by_id(db: Session, service_id: int) -> Optional[Service]:
        return DoorServiceRepository.get_service_by_id(db, service_id)

    @staticmethod
    def get_all_services(db: Session, skip: int = 0, limit: int = 100) -> List[Service]:
        return DoorServiceRepository.get_all_services(db, skip, limit)

    @staticmethod
    def count_services(db: Session) -> int:
        return DoorServiceRepository.count_services(db)

    @staticmethod
    def update_service(db: Session, service_id: int, data: ServiceUpdate, username: str = None) -> Optional[Service]:
        return DoorServiceRepository.update_service(db, service_id, data, username)

    @staticmethod
    def delete_service(db: Session, service_id: int) -> bool:
        return DoorServiceRepository.delete_service(db, service_id)

    # ========================================================================
    # SERVICE OPTION
    # ========================================================================

    @staticmethod
    def create_service_option(db: Session, data: ServiceOptionCreate, username: str = None):
        return DoorServiceRepository.create_service_option(db, data, username)

    @staticmethod
    def get_service_options_by_service(db: Session, service_id: int):
        return DoorServiceRepository.get_service_options_by_service(db, service_id)

    @staticmethod
    def get_service_option_by_id(db: Session, option_id: int):
        return DoorServiceRepository.get_service_option_by_id(db, option_id)

    @staticmethod
    def update_service_option(db: Session, option_id: int, data: ServiceOptionUpdate, username: str = None):
        return DoorServiceRepository.update_service_option(db, option_id, data, username)

    @staticmethod
    def delete_service_option(db: Session, option_id: int):
        return DoorServiceRepository.delete_service_option(db, option_id)

    # ========================================================================
    # SERVICE GROUPING
    # ========================================================================

    @staticmethod
    def create_service_grouping(db: Session, data: ServiceGroupingCreate, username: str = None):
        return DoorServiceRepository.create_service_grouping(db, data, username)

    @staticmethod
    def get_service_grouping_by_id(db: Session, grouping_id: int):
        return DoorServiceRepository.get_service_grouping_by_id(db, grouping_id)

    @staticmethod
    def get_all_service_groupings(db: Session, skip: int = 0, limit: int = 100):
        return DoorServiceRepository.get_all_service_groupings(db, skip, limit)

    @staticmethod
    def count_service_groupings(db: Session):
        return DoorServiceRepository.count_service_groupings(db)

    @staticmethod
    def update_service_grouping(db: Session, grouping_id: int, data: ServiceGroupingUpdate, username: str = None):
        return DoorServiceRepository.update_service_grouping(db, grouping_id, data, username)

    @staticmethod
    def delete_service_grouping(db: Session, grouping_id: int):
        return DoorServiceRepository.delete_service_grouping(db, grouping_id)

    # ========================================================================
    # SERVICE GROUPING CHILD
    # ========================================================================

    @staticmethod
    def create_service_grouping_child(db: Session, data: ServiceGroupingChildCreate, username: str = None):
        return DoorServiceRepository.create_service_grouping_child(db, data, username)

    @staticmethod
    def get_service_grouping_child_by_id(db: Session, child_id: int):
        return DoorServiceRepository.get_service_grouping_child_by_id(db, child_id)

    @staticmethod
    def update_service_grouping_child(db: Session, child_id: int, data: ServiceGroupingChildUpdate, username: str = None):
        return DoorServiceRepository.update_service_grouping_child(db, child_id, data, username)

    @staticmethod
    def delete_service_grouping_child(db: Session, child_id: int):
        return DoorServiceRepository.delete_service_grouping_child(db, child_id)

    # ========================================================================
    # DOOR TYPE SERVICE
    # ========================================================================

    @staticmethod
    def create_door_type_service(db: Session, data: DoorTypeServiceCreate, username: str = None):
        return DoorServiceRepository.create_door_type_service(db, data, username)

    @staticmethod
    def get_door_type_services_by_door_type(db: Session, door_type_id: int):
        return DoorServiceRepository.get_door_type_services_by_door_type(db, door_type_id)

    @staticmethod
    def get_door_type_service_by_id(db: Session, dts_id: int):
        return DoorServiceRepository.get_door_type_service_by_id(db, dts_id)

    @staticmethod
    def update_door_type_service(db: Session, dts_id: int, data: DoorTypeServiceUpdate, username: str = None):
        return DoorServiceRepository.update_door_type_service(db, dts_id, data, username)

    @staticmethod
    def delete_door_type_service(db: Session, dts_id: int):
        return DoorServiceRepository.delete_door_type_service(db, dts_id)

    # ========================================================================
    # UNIT
    # ========================================================================

    @staticmethod
    def create_unit(db: Session, data: UnitCreate, username: str = None) -> Unit:
        return DoorServiceRepository.create_unit(db, data, username)

    @staticmethod
    def get_unit_by_id(db: Session, unit_id: int) -> Optional[Unit]:
        return DoorServiceRepository.get_unit_by_id(db, unit_id)

    @staticmethod
    def get_all_units(db: Session, skip: int = 0, limit: int = 100) -> List[Unit]:
        return DoorServiceRepository.get_all_units(db, skip, limit)

    @staticmethod
    def count_units(db: Session) -> int:
        return DoorServiceRepository.count_units(db)

    @staticmethod
    def update_unit(db: Session, unit_id: int, data: UnitUpdate, username: str = None) -> Optional[Unit]:
        return DoorServiceRepository.update_unit(db, unit_id, data, username)

    @staticmethod
    def delete_unit(db: Session, unit_id: int) -> bool:
        return DoorServiceRepository.delete_unit(db, unit_id)
