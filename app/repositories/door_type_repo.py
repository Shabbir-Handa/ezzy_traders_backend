"""
Door Type Repository
Data access layer for DoorType, ThicknessOption, and DoorTypeService entities.
"""

from sqlalchemy.orm import Session, selectinload
from typing import List, Optional

from app.models import (
    DoorType, DoorTypeThicknessOption, DoorTypeService,
    Service, ServiceOption, ServiceGrouping, ServiceGroupingChild,
)
from app.schemas.door_type import (
    DoorTypeCreate, DoorTypeUpdate,
    DoorTypeThicknessOptionCreate, DoorTypeThicknessOptionUpdate,
    DoorTypeServiceCreate, DoorTypeServiceUpdate,
)


class DoorTypeRepository:

    # ========================================================================
    # DOOR TYPE
    # ========================================================================

    @staticmethod
    def create_door_type(db: Session, data: DoorTypeCreate, username: str = None) -> DoorType:
        door_type = DoorType(
            name=data.name,
            description=data.description,
            created_by=username or "system",
            updated_by=username or "system",
        )
        db.add(door_type)
        db.flush()

        if data.thickness_options:
            for opt in data.thickness_options:
                thickness = DoorTypeThicknessOption(
                    door_type_id=door_type.id,
                    thickness_value=opt.thickness_value,
                    cost_per_sqft=opt.cost_per_sqft,
                    created_by=username or "system",
                    updated_by=username or "system",
                )
                db.add(thickness)

        db.commit()
        db.refresh(door_type)
        return door_type

    @staticmethod
    def get_door_type_by_id(db: Session, door_type_id: int) -> Optional[DoorType]:
        return db.query(DoorType).options(
            selectinload(DoorType.thickness_options),
            selectinload(DoorType.door_type_services).selectinload(DoorTypeService.service).selectinload(Service.options),
            selectinload(DoorType.door_type_services).selectinload(DoorTypeService.service).selectinload(Service.unit),
            selectinload(DoorType.door_type_services).selectinload(DoorTypeService.grouping).selectinload(ServiceGrouping.children).selectinload(ServiceGroupingChild.service).selectinload(Service.options),
        ).filter(DoorType.id == door_type_id).first()

    @staticmethod
    def get_all_door_types(db: Session, skip: int = 0, limit: int = 100) -> List[DoorType]:
        return db.query(DoorType).options(
            selectinload(DoorType.thickness_options),
            selectinload(DoorType.door_type_services).selectinload(DoorTypeService.service).selectinload(Service.options),
            selectinload(DoorType.door_type_services).selectinload(DoorTypeService.service).selectinload(Service.unit),
            selectinload(DoorType.door_type_services).selectinload(DoorTypeService.grouping),
        ).offset(skip).limit(limit).all()

    @staticmethod
    def count_door_types(db: Session) -> int:
        return db.query(DoorType).count()

    @staticmethod
    def update_door_type(db: Session, door_type_id: int, data: DoorTypeUpdate, username: str = None) -> Optional[DoorType]:
        door_type = db.query(DoorType).filter(DoorType.id == door_type_id).first()
        if not door_type:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(door_type, key, value)
        if username:
            door_type.updated_by = username
        db.commit()
        db.refresh(door_type)
        return door_type

    @staticmethod
    def delete_door_type(db: Session, door_type_id: int) -> bool:
        door_type = db.query(DoorType).filter(DoorType.id == door_type_id).first()
        if not door_type:
            return False
        db.delete(door_type)
        db.commit()
        return True

    # ========================================================================
    # DOOR TYPE THICKNESS OPTION
    # ========================================================================

    @staticmethod
    def create_door_type_thickness_option(db: Session, data: DoorTypeThicknessOptionCreate, username: str = None) -> DoorTypeThicknessOption:
        option = DoorTypeThicknessOption(
            door_type_id=data.door_type_id,
            thickness_value=data.thickness_value,
            cost_per_sqft=data.cost_per_sqft,
            created_by=username or "system",
            updated_by=username or "system",
        )
        db.add(option)
        db.commit()
        db.refresh(option)
        return option

    @staticmethod
    def get_door_type_thickness_option_by_id(db: Session, option_id: int) -> Optional[DoorTypeThicknessOption]:
        return db.query(DoorTypeThicknessOption).filter(DoorTypeThicknessOption.id == option_id).first()

    @staticmethod
    def get_door_type_thickness_options_by_door_type(db: Session, door_type_id: int) -> List[DoorTypeThicknessOption]:
        return db.query(DoorTypeThicknessOption).filter(
            DoorTypeThicknessOption.door_type_id == door_type_id
        ).all()

    @staticmethod
    def update_door_type_thickness_option(db: Session, option_id: int, data: DoorTypeThicknessOptionUpdate, username: str = None) -> Optional[DoorTypeThicknessOption]:
        option = db.query(DoorTypeThicknessOption).filter(DoorTypeThicknessOption.id == option_id).first()
        if not option:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(option, key, value)
        if username:
            option.updated_by = username
        db.commit()
        db.refresh(option)
        return option

    @staticmethod
    def delete_door_type_thickness_option(db: Session, option_id: int) -> bool:
        option = db.query(DoorTypeThicknessOption).filter(DoorTypeThicknessOption.id == option_id).first()
        if not option:
            return False
        db.delete(option)
        db.commit()
        return True

    # ========================================================================
    # DOOR TYPE SERVICE
    # ========================================================================

    @staticmethod
    def create_door_type_service(db: Session, data: DoorTypeServiceCreate, username: str = None) -> DoorTypeService:
        dts = DoorTypeService(
            door_type_id=data.door_type_id,
            service_id=data.service_id,
            grouping_id=data.grouping_id,
            required=data.required,
            created_by=username or "system",
            updated_by=username or "system",
        )
        db.add(dts)
        db.commit()
        db.refresh(dts)
        return dts

    @staticmethod
    def get_door_type_services_by_door_type(db: Session, door_type_id: int) -> List[DoorTypeService]:
        return db.query(DoorTypeService).options(
            selectinload(DoorTypeService.service).selectinload(Service.options),
            selectinload(DoorTypeService.service).selectinload(Service.unit),
            selectinload(DoorTypeService.grouping).selectinload(ServiceGrouping.children).selectinload(ServiceGroupingChild.service),
        ).filter(DoorTypeService.door_type_id == door_type_id).all()

    @staticmethod
    def get_door_type_service_by_id(db: Session, dts_id: int) -> Optional[DoorTypeService]:
        return db.query(DoorTypeService).options(
            selectinload(DoorTypeService.service).selectinload(Service.options),
            selectinload(DoorTypeService.grouping),
        ).filter(DoorTypeService.id == dts_id).first()

    @staticmethod
    def update_door_type_service(db: Session, dts_id: int, data: DoorTypeServiceUpdate, username: str = None) -> Optional[DoorTypeService]:
        dts = db.query(DoorTypeService).filter(DoorTypeService.id == dts_id).first()
        if not dts:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(dts, key, value)
        if username:
            dts.updated_by = username
        db.commit()
        db.refresh(dts)
        return dts

    @staticmethod
    def delete_door_type_service(db: Session, dts_id: int) -> bool:
        dts = db.query(DoorTypeService).filter(DoorTypeService.id == dts_id).first()
        if not dts:
            return False
        db.delete(dts)
        db.commit()
        return True
