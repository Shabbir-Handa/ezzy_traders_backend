"""
Quotations API Endpoints
CRUD for: Quotations and Quotation Items
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import math

from app.core.security import get_current_user
from app.db.session import get_db
from app.services.quotation_service import QuotationService
from app.schemas.quotation import (
    QuotationCreate, QuotationUpdate, QuotationResponse,
    QuotationShortResponse, PaginatedQuotationShortResponse,
    QuotationItemCreate, QuotationItemUpdate, QuotationItemResponse,
)

router = APIRouter(prefix="", tags=["Quotations"])


# ============================================================================
# QUOTATIONS
# ============================================================================

@router.get("/quotations", response_model=PaginatedQuotationShortResponse)
async def get_all_quotations(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    total = QuotationService.count_quotations(db)
    skip = (page - 1) * size
    quotations = QuotationService.get_all_quotations(db, skip=skip, limit=size)
    return {
        "data": quotations,
        "total": total,
        "page": page,
        "size": size,
        "pages": math.ceil(total / size) if total > 0 else 1,
    }


@router.get("/quotations/{quotation_id}", response_model=QuotationResponse)
async def get_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    quotation = QuotationService.get_quotation_by_id(db, quotation_id)
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return quotation


@router.get("/quotations/by-number/{quotation_number}", response_model=QuotationResponse)
async def get_quotation_by_number(
    quotation_number: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    quotation = QuotationService.get_quotation_by_number(db, quotation_number)
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return quotation


@router.get("/customers/{customer_id}/quotations")
async def get_customer_quotations(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return QuotationService.get_quotations_by_customer(db, customer_id)


@router.post("/quotations", response_model=QuotationResponse, status_code=status.HTTP_201_CREATED)
async def create_quotation(
    data: QuotationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return QuotationService.create_quotation(db, data, current_user.username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/quotations/{quotation_id}", response_model=QuotationResponse)
async def update_quotation(
    quotation_id: int,
    data: QuotationUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = QuotationService.update_quotation(db, quotation_id, data, current_user.username)
    if not result:
        raise HTTPException(status_code=404, detail="Quotation not found")
    # Return full response
    return QuotationService.get_quotation_by_id(db, quotation_id)


@router.post("/quotations/{quotation_id}/recalculate", response_model=QuotationResponse)
async def recalculate_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = QuotationService.recalculate_quotation_costs(db, quotation_id)
    if not result:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return result


@router.delete("/quotations/{quotation_id}")
async def delete_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not QuotationService.delete_quotation(db, quotation_id):
        raise HTTPException(status_code=404, detail="Quotation not found")
    return {"message": "Quotation deleted"}


# ============================================================================
# QUOTATION ITEMS
# ============================================================================

@router.get("/quotations/{quotation_id}/items")
async def get_quotation_items(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return QuotationService.get_quotation_items_by_quotation(db, quotation_id)


@router.get("/quotation-items/{item_id}", response_model=QuotationItemResponse)
async def get_quotation_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    item = QuotationService.get_quotation_item_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Quotation item not found")
    return item


@router.post("/quotations/{quotation_id}/items", response_model=QuotationItemResponse, status_code=status.HTTP_201_CREATED)
async def create_quotation_item(
    quotation_id: int,
    data: QuotationItemCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    data.quotation_id = quotation_id
    try:
        return QuotationService.create_quotation_item(db, data, current_user.username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/quotation-items/{item_id}", response_model=QuotationItemResponse)
async def update_quotation_item(
    item_id: int,
    data: QuotationItemUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = QuotationService.update_quotation_item(db, item_id, data, current_user.username)
    if not result:
        raise HTTPException(status_code=404, detail="Quotation item not found")
    return result


@router.delete("/quotation-items/{item_id}")
async def delete_quotation_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not QuotationService.delete_quotation_item(db, item_id):
        raise HTTPException(status_code=404, detail="Quotation item not found")
    return {"message": "Quotation item deleted"}
