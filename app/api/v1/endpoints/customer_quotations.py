"""
Customer Quotation API Endpoints
Full CRUD for: Customers, Quotations, Quotation Items
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
import math

from app.core.security import get_current_user
from app.db.session import get_db
from app.services.customer_quotation_service import CustomerQuotationService
from app.schemas.customer import (
    CustomerCreate, CustomerUpdate, CustomerResponse, PaginatedCustomerResponse,
)
from app.schemas.quotation import (
    QuotationCreate, QuotationUpdate, QuotationResponse,
    QuotationShortResponse, PaginatedQuotationShortResponse,
    QuotationItemCreate, QuotationItemUpdate, QuotationItemResponse,
)

router = APIRouter(prefix="", tags=["Customer Quotations"])


# ============================================================================
# CUSTOMERS
# ============================================================================

@router.get("/customers", response_model=PaginatedCustomerResponse)
async def get_all_customers(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    total = CustomerQuotationService.count_customers(db)
    skip = (page - 1) * size
    customers = CustomerQuotationService.get_all_customers(db, skip=skip, limit=size)
    return {
        "data": customers,
        "total": total,
        "page": page,
        "size": size,
        "pages": math.ceil(total / size) if total > 0 else 1,
    }


@router.get("/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    customer = CustomerQuotationService.get_customer_by_id(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return CustomerQuotationService.create_customer(db, data, current_user.username)


@router.patch("/customers/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    data: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = CustomerQuotationService.update_customer(db, customer_id, data, current_user.username)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    return result


@router.delete("/customers/{customer_id}")
async def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not CustomerQuotationService.delete_customer(db, customer_id):
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer deleted"}


# ============================================================================
# QUOTATIONS
# ============================================================================

@router.get("/quotations", response_model=PaginatedQuotationShortResponse)
async def get_all_quotations(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    total = CustomerQuotationService.count_quotations(db)
    skip = (page - 1) * size
    quotations = CustomerQuotationService.get_all_quotations(db, skip=skip, limit=size)
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
    quotation = CustomerQuotationService.get_quotation_by_id(db, quotation_id)
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return quotation


@router.get("/quotations/by-number/{quotation_number}", response_model=QuotationResponse)
async def get_quotation_by_number(
    quotation_number: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    quotation = CustomerQuotationService.get_quotation_by_number(db, quotation_number)
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return quotation


@router.get("/customers/{customer_id}/quotations")
async def get_customer_quotations(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return CustomerQuotationService.get_quotations_by_customer(db, customer_id)


@router.post("/quotations", response_model=QuotationResponse, status_code=status.HTTP_201_CREATED)
async def create_quotation(
    data: QuotationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return CustomerQuotationService.create_quotation(db, data, current_user.username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/quotations/{quotation_id}", response_model=QuotationResponse)
async def update_quotation(
    quotation_id: int,
    data: QuotationUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = CustomerQuotationService.update_quotation(db, quotation_id, data, current_user.username)
    if not result:
        raise HTTPException(status_code=404, detail="Quotation not found")
    # Return full response
    return CustomerQuotationService.get_quotation_by_id(db, quotation_id)


@router.post("/quotations/{quotation_id}/recalculate", response_model=QuotationResponse)
async def recalculate_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = CustomerQuotationService.recalculate_quotation_costs(db, quotation_id)
    if not result:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return result


@router.delete("/quotations/{quotation_id}")
async def delete_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not CustomerQuotationService.delete_quotation(db, quotation_id):
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
    return CustomerQuotationService.get_quotation_items_by_quotation(db, quotation_id)


@router.get("/quotation-items/{item_id}", response_model=QuotationItemResponse)
async def get_quotation_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    item = CustomerQuotationService.get_quotation_item_by_id(db, item_id)
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
        return CustomerQuotationService.create_quotation_item(db, data, current_user.username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/quotation-items/{item_id}", response_model=QuotationItemResponse)
async def update_quotation_item(
    item_id: int,
    data: QuotationItemUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = CustomerQuotationService.update_quotation_item(db, item_id, data, current_user.username)
    if not result:
        raise HTTPException(status_code=404, detail="Quotation item not found")
    return result


@router.delete("/quotation-items/{item_id}")
async def delete_quotation_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not CustomerQuotationService.delete_quotation_item(db, item_id):
        raise HTTPException(status_code=404, detail="Quotation item not found")
    return {"message": "Quotation item deleted"}
