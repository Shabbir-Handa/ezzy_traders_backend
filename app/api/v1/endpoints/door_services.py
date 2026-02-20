"""
Door Services API Endpoints
Full CRUD for: Door Types, Thickness Options, Services, Service Options,
Service Groupings, Grouping Children, Door Type Services, Units
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.security import get_current_user
from app.db.session import get_db
from app.services.door_service_service import DoorServiceService
from app.schemas.door_type import (
    DoorTypeCreate, DoorTypeUpdate, DoorTypeResponse, PaginatedDoorTypeResponse,
    DoorTypeThicknessOptionCreate, DoorTypeThicknessOptionUpdate, DoorTypeThicknessOptionResponse,
    DoorTypeServiceCreate, DoorTypeServiceUpdate, DoorTypeServiceResponse,
)
from app.schemas.service import (
    ServiceCreate, ServiceUpdate, ServiceResponse, PaginatedServiceResponse,
    ServiceOptionCreate, ServiceOptionUpdate, ServiceOptionResponse,
    ServiceGroupingCreate, ServiceGroupingUpdate, ServiceGroupingResponse, PaginatedServiceGroupingResponse,
    ServiceGroupingChildCreate, ServiceGroupingChildUpdate, ServiceGroupingChildResponse,
)
from app.schemas.unit import UnitCreate, UnitUpdate, UnitResponse

import math

router = APIRouter(prefix="", tags=["Door Services"])


# ============================================================================
# DOOR TYPES
# ============================================================================

@router.get("/door-types", response_model=PaginatedDoorTypeResponse)
async def get_all_door_types(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    total = DoorServiceService.count_door_types(db)
    skip = (page - 1) * size
    door_types = DoorServiceService.get_all_door_types(db, skip=skip, limit=size)
    return {
        "data": door_types,
        "total": total,
        "page": page,
        "size": size,
        "pages": math.ceil(total / size) if total > 0 else 1,
    }


@router.get("/door-types/{door_type_id}", response_model=DoorTypeResponse)
async def get_door_type(
    door_type_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    door_type = DoorServiceService.get_door_type_by_id(db, door_type_id)
    if not door_type:
        raise HTTPException(status_code=404, detail="Door type not found")
    return door_type


@router.post("/door-types", response_model=DoorTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_door_type(
    data: DoorTypeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return DoorServiceService.create_door_type(db, data, current_user.username)


@router.patch("/door-types/{door_type_id}", response_model=DoorTypeResponse)
async def update_door_type(
    door_type_id: int,
    data: DoorTypeUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = DoorServiceService.update_door_type(db, door_type_id, data, current_user.username)
    if not result:
        raise HTTPException(status_code=404, detail="Door type not found")
    return result


@router.delete("/door-types/{door_type_id}")
async def delete_door_type(
    door_type_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not DoorServiceService.delete_door_type(db, door_type_id):
        raise HTTPException(status_code=404, detail="Door type not found")
    return {"message": "Door type deleted"}


# ============================================================================
# THICKNESS OPTIONS
# ============================================================================

@router.get("/door-types/{door_type_id}/thickness-options")
async def get_thickness_options(
    door_type_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return DoorServiceService.get_door_type_thickness_options_by_door_type(db, door_type_id)


@router.post("/door-types/{door_type_id}/thickness-options", response_model=DoorTypeThicknessOptionResponse, status_code=status.HTTP_201_CREATED)
async def create_thickness_option(
    door_type_id: int,
    data: DoorTypeThicknessOptionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    data.door_type_id = door_type_id
    return DoorServiceService.create_door_type_thickness_option(db, data, current_user.username)


@router.patch("/thickness-options/{option_id}", response_model=DoorTypeThicknessOptionResponse)
async def update_thickness_option(
    option_id: int,
    data: DoorTypeThicknessOptionUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = DoorServiceService.update_door_type_thickness_option(db, option_id, data, current_user.username)
    if not result:
        raise HTTPException(status_code=404, detail="Thickness option not found")
    return result


@router.delete("/thickness-options/{option_id}")
async def delete_thickness_option(
    option_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not DoorServiceService.delete_door_type_thickness_option(db, option_id):
        raise HTTPException(status_code=404, detail="Thickness option not found")
    return {"message": "Thickness option deleted"}


# ============================================================================
# SERVICES
# ============================================================================

@router.get("/services", response_model=PaginatedServiceResponse)
async def get_all_services(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    total = DoorServiceService.count_services(db)
    skip = (page - 1) * size
    services = DoorServiceService.get_all_services(db, skip=skip, limit=size)
    return {
        "data": services,
        "total": total,
        "page": page,
        "size": size,
        "pages": math.ceil(total / size) if total > 0 else 1,
    }


@router.get("/services/{service_id}", response_model=ServiceResponse)
async def get_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = DoorServiceService.get_service_by_id(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.post("/services", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_service(
    data: ServiceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return DoorServiceService.create_service(db, data, current_user.username)


@router.patch("/services/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: int,
    data: ServiceUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = DoorServiceService.update_service(db, service_id, data, current_user.username)
    if not result:
        raise HTTPException(status_code=404, detail="Service not found")
    return result


@router.delete("/services/{service_id}")
async def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not DoorServiceService.delete_service(db, service_id):
        raise HTTPException(status_code=404, detail="Service not found")
    return {"message": "Service deleted"}


# ============================================================================
# SERVICE OPTIONS
# ============================================================================

@router.get("/services/{service_id}/options")
async def get_service_options(
    service_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return DoorServiceService.get_service_options_by_service(db, service_id)


@router.post("/services/{service_id}/options", response_model=ServiceOptionResponse, status_code=status.HTTP_201_CREATED)
async def create_service_option(
    service_id: int,
    data: ServiceOptionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    data.service_id = service_id
    return DoorServiceService.create_service_option(db, data, current_user.username)


@router.patch("/service-options/{option_id}", response_model=ServiceOptionResponse)
async def update_service_option(
    option_id: int,
    data: ServiceOptionUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = DoorServiceService.update_service_option(db, option_id, data, current_user.username)
    if not result:
        raise HTTPException(status_code=404, detail="Service option not found")
    return result


@router.delete("/service-options/{option_id}")
async def delete_service_option(
    option_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not DoorServiceService.delete_service_option(db, option_id):
        raise HTTPException(status_code=404, detail="Service option not found")
    return {"message": "Service option deleted"}


# ============================================================================
# SERVICE GROUPINGS
# ============================================================================

@router.get("/service-groupings", response_model=PaginatedServiceGroupingResponse)
async def get_all_service_groupings(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    total = DoorServiceService.count_service_groupings(db)
    skip = (page - 1) * size
    groupings = DoorServiceService.get_all_service_groupings(db, skip=skip, limit=size)
    return {
        "data": groupings,
        "total": total,
        "page": page,
        "size": size,
        "pages": math.ceil(total / size) if total > 0 else 1,
    }


@router.get("/service-groupings/{grouping_id}", response_model=ServiceGroupingResponse)
async def get_service_grouping(
    grouping_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    grouping = DoorServiceService.get_service_grouping_by_id(db, grouping_id)
    if not grouping:
        raise HTTPException(status_code=404, detail="Service grouping not found")
    return grouping


@router.post("/service-groupings", response_model=ServiceGroupingResponse, status_code=status.HTTP_201_CREATED)
async def create_service_grouping(
    data: ServiceGroupingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return DoorServiceService.create_service_grouping(db, data, current_user.username)


@router.patch("/service-groupings/{grouping_id}", response_model=ServiceGroupingResponse)
async def update_service_grouping(
    grouping_id: int,
    data: ServiceGroupingUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = DoorServiceService.update_service_grouping(db, grouping_id, data, current_user.username)
    if not result:
        raise HTTPException(status_code=404, detail="Service grouping not found")
    return result


@router.delete("/service-groupings/{grouping_id}")
async def delete_service_grouping(
    grouping_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not DoorServiceService.delete_service_grouping(db, grouping_id):
        raise HTTPException(status_code=404, detail="Service grouping not found")
    return {"message": "Service grouping deleted"}


# ============================================================================
# SERVICE GROUPING CHILDREN
# ============================================================================

@router.post("/service-groupings/{grouping_id}/children", response_model=ServiceGroupingChildResponse, status_code=status.HTTP_201_CREATED)
async def create_service_grouping_child(
    grouping_id: int,
    data: ServiceGroupingChildCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    data.grouping_id = grouping_id
    return DoorServiceService.create_service_grouping_child(db, data, current_user.username)


@router.patch("/service-grouping-children/{child_id}", response_model=ServiceGroupingChildResponse)
async def update_service_grouping_child(
    child_id: int,
    data: ServiceGroupingChildUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = DoorServiceService.update_service_grouping_child(db, child_id, data, current_user.username)
    if not result:
        raise HTTPException(status_code=404, detail="Service grouping child not found")
    return result


@router.delete("/service-grouping-children/{child_id}")
async def delete_service_grouping_child(
    child_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not DoorServiceService.delete_service_grouping_child(db, child_id):
        raise HTTPException(status_code=404, detail="Service grouping child not found")
    return {"message": "Service grouping child deleted"}


# ============================================================================
# DOOR TYPE SERVICES
# ============================================================================

@router.get("/door-types/{door_type_id}/services")
async def get_door_type_services(
    door_type_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return DoorServiceService.get_door_type_services_by_door_type(db, door_type_id)


@router.post("/door-types/{door_type_id}/services", response_model=DoorTypeServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_door_type_service(
    door_type_id: int,
    data: DoorTypeServiceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    data.door_type_id = door_type_id
    return DoorServiceService.create_door_type_service(db, data, current_user.username)


@router.patch("/door-type-services/{dts_id}", response_model=DoorTypeServiceResponse)
async def update_door_type_service(
    dts_id: int,
    data: DoorTypeServiceUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = DoorServiceService.update_door_type_service(db, dts_id, data, current_user.username)
    if not result:
        raise HTTPException(status_code=404, detail="Door type service association not found")
    return result


@router.delete("/door-type-services/{dts_id}")
async def delete_door_type_service(
    dts_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not DoorServiceService.delete_door_type_service(db, dts_id):
        raise HTTPException(status_code=404, detail="Door type service association not found")
    return {"message": "Door type service deleted"}


# ============================================================================
# UNITS
# ============================================================================

@router.get("/units")
async def get_all_units(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return DoorServiceService.get_all_units(db)


@router.get("/units/{unit_id}", response_model=UnitResponse)
async def get_unit(
    unit_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    unit = DoorServiceService.get_unit_by_id(db, unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return unit


@router.post("/units", response_model=UnitResponse, status_code=status.HTTP_201_CREATED)
async def create_unit(
    data: UnitCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return DoorServiceService.create_unit(db, data, current_user.username)


@router.patch("/units/{unit_id}", response_model=UnitResponse)
async def update_unit(
    unit_id: int,
    data: UnitUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = DoorServiceService.update_unit(db, unit_id, data, current_user.username)
    if not result:
        raise HTTPException(status_code=404, detail="Unit not found")
    return result


@router.delete("/units/{unit_id}")
async def delete_unit(
    unit_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not DoorServiceService.delete_unit(db, unit_id):
        raise HTTPException(status_code=404, detail="Unit not found")
    return {"message": "Unit deleted"}
