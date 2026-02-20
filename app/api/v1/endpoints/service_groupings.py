"""
Service Groupings API Endpoints
CRUD for: Service Groupings and Grouping Children
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import math

from app.core.security import get_current_user
from app.db.session import get_db
from app.services.service_grouping_service import ServiceGroupingService
from app.schemas.service import (
    ServiceGroupingCreate, ServiceGroupingUpdate, ServiceGroupingResponse, PaginatedServiceGroupingResponse,
    ServiceGroupingChildCreate, ServiceGroupingChildUpdate, ServiceGroupingChildResponse,
)

router = APIRouter(prefix="", tags=["Service Groupings"])


# ============================================================================
# SERVICE GROUPINGS
# ============================================================================

@router.get("/service-groupings", response_model=PaginatedServiceGroupingResponse)
async def get_all_service_groupings(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    total = ServiceGroupingService.count_service_groupings(db)
    skip = (page - 1) * size
    groupings = ServiceGroupingService.get_all_service_groupings(db, skip=skip, limit=size)
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
    grouping = ServiceGroupingService.get_service_grouping_by_id(db, grouping_id)
    if not grouping:
        raise HTTPException(status_code=404, detail="Service grouping not found")
    return grouping


@router.post("/service-groupings", response_model=ServiceGroupingResponse, status_code=status.HTTP_201_CREATED)
async def create_service_grouping(
    data: ServiceGroupingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return ServiceGroupingService.create_service_grouping(db, data, current_user.username)


@router.patch("/service-groupings/{grouping_id}", response_model=ServiceGroupingResponse)
async def update_service_grouping(
    grouping_id: int,
    data: ServiceGroupingUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = ServiceGroupingService.update_service_grouping(db, grouping_id, data, current_user.username)
    if not result:
        raise HTTPException(status_code=404, detail="Service grouping not found")
    return result


@router.delete("/service-groupings/{grouping_id}")
async def delete_service_grouping(
    grouping_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not ServiceGroupingService.delete_service_grouping(db, grouping_id):
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
    return ServiceGroupingService.create_service_grouping_child(db, data, current_user.username)


@router.patch("/service-grouping-children/{child_id}", response_model=ServiceGroupingChildResponse)
async def update_service_grouping_child(
    child_id: int,
    data: ServiceGroupingChildUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = ServiceGroupingService.update_service_grouping_child(db, child_id, data, current_user.username)
    if not result:
        raise HTTPException(status_code=404, detail="Service grouping child not found")
    return result


@router.delete("/service-grouping-children/{child_id}")
async def delete_service_grouping_child(
    child_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not ServiceGroupingService.delete_service_grouping_child(db, child_id):
        raise HTTPException(status_code=404, detail="Service grouping child not found")
    return {"message": "Service grouping child deleted"}
