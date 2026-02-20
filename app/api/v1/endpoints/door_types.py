"""
Door Types API Endpoints
CRUD for: Door Types, Thickness Options, Door Type Services
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import math

from app.core.security import get_current_user
from app.db.session import get_db
from app.services.door_type_service import DoorTypeService
from app.schemas.door_type import (
    DoorTypeCreate, DoorTypeUpdate, DoorTypeResponse, PaginatedDoorTypeResponse,
    DoorTypeThicknessOptionCreate, DoorTypeThicknessOptionUpdate, DoorTypeThicknessOptionResponse,
    DoorTypeServiceCreate, DoorTypeServiceUpdate, DoorTypeServiceResponse,
)

router = APIRouter(prefix="", tags=["Door Types"])


# ============================================================================
# DOOR TYPES
# ============================================================================

@router.get("/door-types", response_model=PaginatedDoorTypeResponse)
async def get_all_door_types(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    total = DoorTypeService.count_door_types(db)
    skip = (page - 1) * size
    door_types = DoorTypeService.get_all_door_types(db, skip=skip, limit=size)
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
    door_type = DoorTypeService.get_door_type_by_id(db, door_type_id)
    if not door_type:
        raise HTTPException(status_code=404, detail="Door type not found")
    return door_type


@router.post("/door-types", response_model=DoorTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_door_type(
    data: DoorTypeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return DoorTypeService.create_door_type(db, data, current_user.username)


@router.patch("/door-types/{door_type_id}", response_model=DoorTypeResponse)
async def update_door_type(
    door_type_id: int,
    data: DoorTypeUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = DoorTypeService.update_door_type(db, door_type_id, data, current_user.username)
    if not result:
        raise HTTPException(status_code=404, detail="Door type not found")
    return result


@router.delete("/door-types/{door_type_id}")
async def delete_door_type(
    door_type_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not DoorTypeService.delete_door_type(db, door_type_id):
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
    return DoorTypeService.get_door_type_thickness_options_by_door_type(db, door_type_id)


@router.post("/door-types/{door_type_id}/thickness-options", response_model=DoorTypeThicknessOptionResponse, status_code=status.HTTP_201_CREATED)
async def create_thickness_option(
    door_type_id: int,
    data: DoorTypeThicknessOptionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    data.door_type_id = door_type_id
    return DoorTypeService.create_door_type_thickness_option(db, data, current_user.username)


@router.patch("/thickness-options/{option_id}", response_model=DoorTypeThicknessOptionResponse)
async def update_thickness_option(
    option_id: int,
    data: DoorTypeThicknessOptionUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = DoorTypeService.update_door_type_thickness_option(db, option_id, data, current_user.username)
    if not result:
        raise HTTPException(status_code=404, detail="Thickness option not found")
    return result


@router.delete("/thickness-options/{option_id}")
async def delete_thickness_option(
    option_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not DoorTypeService.delete_door_type_thickness_option(db, option_id):
        raise HTTPException(status_code=404, detail="Thickness option not found")
    return {"message": "Thickness option deleted"}


# ============================================================================
# DOOR TYPE SERVICES
# ============================================================================

@router.get("/door-types/{door_type_id}/services")
async def get_door_type_services(
    door_type_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return DoorTypeService.get_door_type_services_by_door_type(db, door_type_id)


@router.post("/door-types/{door_type_id}/services", response_model=DoorTypeServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_door_type_service(
    door_type_id: int,
    data: DoorTypeServiceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    data.door_type_id = door_type_id
    return DoorTypeService.create_door_type_service_link(db, data, current_user.username)


@router.patch("/door-type-services/{dts_id}", response_model=DoorTypeServiceResponse)
async def update_door_type_service(
    dts_id: int,
    data: DoorTypeServiceUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = DoorTypeService.update_door_type_service(db, dts_id, data, current_user.username)
    if not result:
        raise HTTPException(status_code=404, detail="Door type service association not found")
    return result


@router.delete("/door-type-services/{dts_id}")
async def delete_door_type_service(
    dts_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not DoorTypeService.delete_door_type_service(db, dts_id):
        raise HTTPException(status_code=404, detail="Door type service association not found")
    return {"message": "Door type service deleted"}
