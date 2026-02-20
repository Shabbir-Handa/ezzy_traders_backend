"""
Service Repository
Data access layer for Service and ServiceOption entities.
"""

from sqlalchemy.orm import Session, selectinload
from typing import List, Optional

from app.models import Service, ServiceOption
from app.schemas.service import (
    ServiceCreate, ServiceUpdate,
    ServiceOptionCreate, ServiceOptionUpdate,
)


class ServiceRepository:

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
