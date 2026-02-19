"""
Customer & Quotation Management Endpoints
Routes contain NO business logic — all logic delegated to services.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.services.customer_quotation_service import CustomerQuotationService
from app.schemas.customer import (
    CustomerCreate, CustomerUpdate, CustomerResponse, PaginatedCustomerResponse
)
from app.schemas.quotation import (
    QuotationCreate, QuotationUpdate, QuotationResponse,
    QuotationShortResponse, PaginatedQuotationShortResponse,
    QuotationItemCreate, QuotationItemUpdate, QuotationItemResponse,
    QuotationItemAttributeCreate
)
from app.core.security import get_current_user
from app.db.session import get_db

router = APIRouter(tags=["Customer-Quotation-Management"])


# ============================================================================
# CUSTOMER ENDPOINTS
# ============================================================================

@router.post("/customers/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
        customer_data: CustomerCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Create a new customer"""
    try:
        customer = CustomerQuotationService.create_customer(db, customer_data, current_user.username)
        db.commit()
        return customer
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.get("/customers/", response_model=PaginatedCustomerResponse)
def get_customers(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get all customers with pagination"""
    try:
        customers = CustomerQuotationService.get_all_customers(db, skip=skip, limit=limit)
        total = CustomerQuotationService.count_customers(db)

        return {
            "data": customers,
            "total": total,
            "page": (skip // limit) + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.get("/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(
        customer_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get a specific customer by ID"""
    try:
        customer = CustomerQuotationService.get_customer_by_id(db, customer_id)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        return customer
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.put("/customers/{customer_id}", response_model=CustomerResponse)
def update_customer(
        customer_id: int,
        customer_data: CustomerUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Update a customer"""
    try:
        customer = CustomerQuotationService.update_customer(db, customer_id, customer_data, current_user.username)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        db.commit()
        return customer
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.delete("/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
        customer_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Delete a customer"""
    try:
        success = CustomerQuotationService.delete_customer(db, customer_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        db.commit()
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


# ============================================================================
# QUOTATION ENDPOINTS
# ============================================================================

@router.post("/quotations/", response_model=QuotationResponse, status_code=status.HTTP_201_CREATED)
def create_quotation(
        quotation_data: QuotationCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Create a new quotation with items and attributes"""
    try:
        quotation = CustomerQuotationService.create_quotation(db, quotation_data, current_user.username)
        db.commit()
        # Re-read to get full join-loaded data
        quotation = CustomerQuotationService.get_quotation_by_id(db, quotation.id)
        return quotation
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.get("/quotations/", response_model=PaginatedQuotationShortResponse)
def get_quotations(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get all quotations with pagination"""
    try:
        quotations = CustomerQuotationService.get_all_quotations(db, skip=skip, limit=limit)
        total = CustomerQuotationService.count_quotations(db)

        return {
            "data": quotations,
            "total": total,
            "page": (skip // limit) + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.get("/quotations/{quotation_id}", response_model=QuotationResponse)
def get_quotation(
        quotation_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get a specific quotation by ID with full details"""
    try:
        quotation = CustomerQuotationService.get_quotation_by_id(db, quotation_id)
        if not quotation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quotation not found")
        return quotation
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.get("/quotations/by-number/{quotation_number}", response_model=QuotationResponse)
def get_quotation_by_number(
        quotation_number: str,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get a specific quotation by quotation number"""
    try:
        quotation = CustomerQuotationService.get_quotation_by_number(db, quotation_number)
        if not quotation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quotation not found")
        return quotation
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.get("/customers/{customer_id}/quotations", response_model=List[QuotationResponse])
def get_customer_quotations(
        customer_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get all quotations for a specific customer"""
    try:
        quotations = CustomerQuotationService.get_quotations_by_customer(db, customer_id)
        return quotations
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.put("/quotations/{quotation_id}", response_model=QuotationResponse)
def update_quotation(
        quotation_id: int,
        quotation_data: QuotationUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Update a quotation"""
    try:
        quotation = CustomerQuotationService.update_quotation(db, quotation_id, quotation_data, current_user.username)
        if not quotation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quotation not found")
        db.commit()
        quotation = CustomerQuotationService.get_quotation_by_id(db, quotation.id)
        return quotation
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.delete("/quotations/{quotation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quotation(
        quotation_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Delete a quotation"""
    try:
        success = CustomerQuotationService.delete_quotation(db, quotation_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quotation not found")
        db.commit()
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.post("/quotations/{quotation_id}/recalculate", response_model=QuotationResponse)
def recalculate_quotation_costs(
        quotation_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Recalculate all costs for a quotation"""
    try:
        quotation = CustomerQuotationService.recalculate_quotation_costs(db, quotation_id)
        db.commit()
        quotation = CustomerQuotationService.get_quotation_by_id(db, quotation.id)
        return quotation
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


# ============================================================================
# QUOTATION ITEM ENDPOINTS
# ============================================================================

@router.post("/quotation-items/", response_model=QuotationItemResponse, status_code=status.HTTP_201_CREATED)
def create_quotation_item(
        item_data: QuotationItemCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Create a new quotation item"""
    try:
        item = CustomerQuotationService.create_quotation_item(db, item_data, current_user.username)
        db.commit()
        item = CustomerQuotationService.get_quotation_item_by_id(db, item.id)
        return item
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.get("/quotation-items/{item_id}", response_model=QuotationItemResponse)
def get_quotation_item(
        item_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get a specific quotation item by ID"""
    try:
        item = CustomerQuotationService.get_quotation_item_by_id(db, item_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quotation item not found")
        return item
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.get("/quotations/{quotation_id}/items", response_model=List[QuotationItemResponse])
def get_quotation_items(
        quotation_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get all items for a specific quotation"""
    try:
        items = CustomerQuotationService.get_quotation_items_by_quotation(db, quotation_id)
        return items
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.put("/quotation-items/{item_id}", response_model=QuotationItemResponse)
def update_quotation_item(
        item_id: int,
        item_data: QuotationItemUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Update a quotation item"""
    try:
        item = CustomerQuotationService.update_quotation_item(db, item_id, item_data, current_user.username)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quotation item not found")
        db.commit()
        item = CustomerQuotationService.get_quotation_item_by_id(db, item.id)
        return item
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.delete("/quotation-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quotation_item(
        item_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Delete a quotation item"""
    try:
        success = CustomerQuotationService.delete_quotation_item(db, item_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quotation item not found")
        db.commit()
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")
