"""
Services API Endpoints
CRUD for: Services and Service Options
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import math

from app.core.security import get_current_user
from app.db.session import get_db
from app.services.service_service import ServiceService
from app.schemas.service import (
    ServiceCreate, ServiceUpdate, ServiceResponse, PaginatedServiceResponse,
    ServiceOptionCreate, ServiceOptionUpdate, ServiceOptionResponse,
)

router = APIRouter(prefix="", tags=["Services"])


# ============================================================================
# SERVICES
# ============================================================================

@router.get("/services", response_model=PaginatedServiceResponse)
async def get_all_services(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    total = ServiceService.count_services(db)
    skip = (page - 1) * size
    services = ServiceService.get_all_services(db, skip=skip, limit=size)
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
    service = ServiceService.get_service_by_id(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.post("/services", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_service(
    data: ServiceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return ServiceService.create_service(db, data, current_user.username)


@router.patch("/services/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: int,
    data: ServiceUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = ServiceService.update_service(db, service_id, data, current_user.username)
    if not result:
        raise HTTPException(status_code=404, detail="Service not found")
    return result


@router.delete("/services/{service_id}")
async def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not ServiceService.delete_service(db, service_id):
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
    return ServiceService.get_service_options_by_service(db, service_id)


@router.post("/services/{service_id}/options", response_model=ServiceOptionResponse, status_code=status.HTTP_201_CREATED)
async def create_service_option(
    service_id: int,
    data: ServiceOptionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    data.service_id = service_id
    return ServiceService.create_service_option(db, data, current_user.username)


@router.patch("/service-options/{option_id}", response_model=ServiceOptionResponse)
async def update_service_option(
    option_id: int,
    data: ServiceOptionUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = ServiceService.update_service_option(db, option_id, data, current_user.username)
    if not result:
        raise HTTPException(status_code=404, detail="Service option not found")
    return result


@router.delete("/service-options/{option_id}")
async def delete_service_option(
    option_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not ServiceService.delete_service_option(db, option_id):
        raise HTTPException(status_code=404, detail="Service option not found")
    return {"message": "Service option deleted"}
