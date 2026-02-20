"""
Units API Endpoints
CRUD for: Units
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.services.unit_service import UnitService
from app.schemas.unit import UnitCreate, UnitUpdate, UnitResponse

router = APIRouter(prefix="", tags=["Units"])


@router.get("/units")
async def get_all_units(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return UnitService.get_all_units(db)


@router.get("/units/{unit_id}", response_model=UnitResponse)
async def get_unit(
    unit_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    unit = UnitService.get_unit_by_id(db, unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return unit


@router.post("/units", response_model=UnitResponse, status_code=status.HTTP_201_CREATED)
async def create_unit(
    data: UnitCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return UnitService.create_unit(db, data, current_user.username)


@router.patch("/units/{unit_id}", response_model=UnitResponse)
async def update_unit(
    unit_id: int,
    data: UnitUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = UnitService.update_unit(db, unit_id, data, current_user.username)
    if not result:
        raise HTTPException(status_code=404, detail="Unit not found")
    return result


@router.delete("/units/{unit_id}")
async def delete_unit(
    unit_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not UnitService.delete_unit(db, unit_id):
        raise HTTPException(status_code=404, detail="Unit not found")
    return {"message": "Unit deleted"}
