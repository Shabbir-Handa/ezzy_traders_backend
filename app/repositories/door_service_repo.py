"""
Door & Service Repository
Data access layer for DoorType, Service, ServiceGrouping, Unit, and related entities.
"""

from sqlalchemy.orm import Session, joinedload, selectinload
from typing import List, Optional

from app.models import (
    DoorType, DoorTypeThicknessOption, DoorTypeService,
    Service, ServiceOption, ServiceGrouping, ServiceGroupingChild,
    Unit,
)
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


class DoorServiceRepository:

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
    # SERVICE
    # ========================================================================

    @staticmethod
    def create_service(db: Session, data: ServiceCreate, username: str = None) -> Service:
        service = Service(
            name=data.name,
            description=data.description,
            service_type=data.service_type.value,
            consumable_kind=data.consumable_kind.value if data.consumable_kind else None,
            cost=data.cost,
            both_sides=data.both_sides,
            unit_id=data.unit_id,
            created_by=username or "system",
            updated_by=username or "system",
        )
        db.add(service)
        db.flush()

        if data.options:
            for opt_data in data.options:
                option = ServiceOption(
                    service_id=service.id,
                    name=opt_data.name,
                    description=opt_data.description,
                    cost=opt_data.cost,
                    created_by=username or "system",
                    updated_by=username or "system",
                )
                db.add(option)

        db.commit()
        db.refresh(service)
        return service

    @staticmethod
    def get_service_by_id(db: Session, service_id: int) -> Optional[Service]:
        return db.query(Service).options(
            selectinload(Service.options),
            selectinload(Service.unit),
        ).filter(Service.id == service_id).first()

    @staticmethod
    def get_all_services(db: Session, skip: int = 0, limit: int = 100) -> List[Service]:
        return db.query(Service).options(
            selectinload(Service.options),
            selectinload(Service.unit),
        ).offset(skip).limit(limit).all()

    @staticmethod
    def count_services(db: Session) -> int:
        return db.query(Service).count()

    @staticmethod
    def update_service(db: Session, service_id: int, data: ServiceUpdate, username: str = None) -> Optional[Service]:
        service = db.query(Service).filter(Service.id == service_id).first()
        if not service:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == 'service_type' and value is not None:
                value = value.value if hasattr(value, 'value') else value
            if key == 'consumable_kind' and value is not None:
                value = value.value if hasattr(value, 'value') else value
            setattr(service, key, value)
        if username:
            service.updated_by = username
        db.commit()
        db.refresh(service)
        return service

    @staticmethod
    def delete_service(db: Session, service_id: int) -> bool:
        service = db.query(Service).filter(Service.id == service_id).first()
        if not service:
            return False
        db.delete(service)
        db.commit()
        return True

    # ========================================================================
    # SERVICE OPTION
    # ========================================================================

    @staticmethod
    def create_service_option(db: Session, data: ServiceOptionCreate, username: str = None) -> ServiceOption:
        option = ServiceOption(
            service_id=data.service_id,
            name=data.name,
            description=data.description,
            cost=data.cost,
            created_by=username or "system",
            updated_by=username or "system",
        )
        db.add(option)
        db.commit()
        db.refresh(option)
        return option

    @staticmethod
    def get_service_options_by_service(db: Session, service_id: int) -> List[ServiceOption]:
        return db.query(ServiceOption).filter(ServiceOption.service_id == service_id).all()

    @staticmethod
    def get_service_option_by_id(db: Session, option_id: int) -> Optional[ServiceOption]:
        return db.query(ServiceOption).filter(ServiceOption.id == option_id).first()

    @staticmethod
    def update_service_option(db: Session, option_id: int, data: ServiceOptionUpdate, username: str = None) -> Optional[ServiceOption]:
        option = db.query(ServiceOption).filter(ServiceOption.id == option_id).first()
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
    def delete_service_option(db: Session, option_id: int) -> bool:
        option = db.query(ServiceOption).filter(ServiceOption.id == option_id).first()
        if not option:
            return False
        db.delete(option)
        db.commit()
        return True

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

    # ========================================================================
    # UNIT
    # ========================================================================

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
