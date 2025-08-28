"""
Customer and Quotation Management Router
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from dependencies import get_db, get_current_user
from db_helper.customer_quotation_crud import CustomerQuotationCRUD
from schemas.schemas import (
    CustomerCreate, CustomerUpdate, CustomerResponse,
    QuotationCreate, QuotationUpdate, QuotationResponse,
    QuotationItemCreate, QuotationItemUpdate, QuotationItemResponse,
    QuotationItemAttributeCreate, QuotationItemAttributeUpdate, QuotationItemAttributeResponse,
    ComprehensiveQuotationCreate
)

router = APIRouter(
    prefix="/customer-quotation",
    tags=["Customer & Quotation Management"],
)

# ============================================================================
# CUSTOMER ENDPOINTS
# ============================================================================

@router.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new customer"""
    try:
        # Check if customer email already exists
        if customer_data.email:
            existing_customer = CustomerQuotationCRUD.get_customer_by_email(db, customer_data.email)
            if existing_customer:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Customer with this email already exists"
                )
        
        # Check if customer phone already exists
        if customer_data.phone:
            existing_customer = CustomerQuotationCRUD.get_customer_by_phone(db, customer_data.phone)
            if existing_customer:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Customer with this phone already exists"
                )
        
        customer = CustomerQuotationCRUD.create_customer(db, customer_data, created_by=current_user.username)
        return customer
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )

@router.get("/customers", response_model=List[CustomerResponse])
def get_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all customers with pagination and optional search"""
    try:
        if search:
            customers = CustomerQuotationCRUD.search_customers(db, search)
        elif active_only:
            customers = CustomerQuotationCRUD.get_active_customers(db)
        else:
            customers = CustomerQuotationCRUD.get_all_customers(db, skip=skip, limit=limit)
        return customers
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )

@router.get("/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific customer by ID"""
    try:
        customer = CustomerQuotationCRUD.get_customer_by_id(db, customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        return customer
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )

@router.put("/customers/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a customer"""
    try:
        customer = CustomerQuotationCRUD.update_customer(db, customer_id, customer_data, updated_by=current_user.username)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        return customer
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )

@router.delete("/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a customer (soft delete)"""
    try:
        success = CustomerQuotationCRUD.delete_customer(db, customer_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )

# ============================================================================
# QUOTATION ENDPOINTS
# ============================================================================

@router.post("/quotations", response_model=QuotationResponse, status_code=status.HTTP_201_CREATED)
def create_quotation(
    quotation_data: QuotationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new quotation"""
    try:
        # Generate quotation number if not provided
        if not quotation_data.quotation_number:
            quotation_data.quotation_number = CustomerQuotationCRUD.generate_quotation_number(db)
        
        # Set employee IDs
        quotation_data.created_by_employee_id = current_user.id
        quotation_data.updated_by_employee_id = current_user.id
        
        quotation = CustomerQuotationCRUD.create_quotation(db, quotation_data, created_by=current_user.username)
        return quotation
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


@router.post("/quotations/comprehensive", response_model=QuotationResponse, status_code=status.HTTP_201_CREATED)
def create_comprehensive_quotation(
    quotation_data: ComprehensiveQuotationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a complete quotation with items and attributes in one request"""
    try:
        # Set employee IDs
        quotation_data.created_by_employee_id = current_user.id
        quotation_data.updated_by_employee_id = current_user.id
        
        quotation = CustomerQuotationCRUD.create_comprehensive_quotation(
            db, quotation_data, created_by=current_user.username
        )
        return quotation
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )

@router.get("/quotations", response_model=List[QuotationResponse])
def get_quotations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    customer_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all quotations with pagination and optional filtering"""
    try:
        if customer_id:
            quotations = CustomerQuotationCRUD.get_quotations_by_customer(db, customer_id)
        elif status:
            quotations = CustomerQuotationCRUD.get_quotations_by_status(db, status)
        elif active_only:
            quotations = CustomerQuotationCRUD.get_all_quotations(db, skip=skip, limit=limit)
        else:
            quotations = CustomerQuotationCRUD.get_all_quotations(db, skip=skip, limit=limit)
        return quotations
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )

@router.get("/quotations/{quotation_id}", response_model=QuotationResponse)
def get_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific quotation by ID"""
    try:
        quotation = CustomerQuotationCRUD.get_quotation_by_id(db, quotation_id)
        if not quotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quotation not found"
            )
        return quotation
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )

@router.put("/quotations/{quotation_id}", response_model=QuotationResponse)
def update_quotation(
    quotation_id: int,
    quotation_data: QuotationUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a quotation"""
    try:
        # Set updated by employee ID
        quotation_data.updated_by_employee_id = current_user.id
        
        quotation = CustomerQuotationCRUD.update_quotation(db, quotation_id, quotation_data, updated_by=current_user.username)
        if not quotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quotation not found"
            )
        return quotation
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )

@router.delete("/quotations/{quotation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a quotation (soft delete)"""
    try:
        success = CustomerQuotationCRUD.delete_quotation(db, quotation_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quotation not found"
            )
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )

@router.get("/quotations/{quotation_id}/summary")
def get_quotation_summary(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get quotation summary with totals"""
    try:
        summary = CustomerQuotationCRUD.get_quotation_summary(db, quotation_id)
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quotation not found"
            )
        return summary
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )

# ============================================================================
# QUOTATION ITEM ENDPOINTS
# ============================================================================

@router.post("/quotation-items", response_model=QuotationItemResponse, status_code=status.HTTP_201_CREATED)
def create_quotation_item(
    item_data: QuotationItemCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new quotation item"""
    try:
        quotation_item = CustomerQuotationCRUD.create_quotation_item(db, item_data, created_by=current_user.username)
        return quotation_item
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )

@router.get("/quotation-items", response_model=List[QuotationItemResponse])
def get_quotation_items(
    quotation_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all items for a specific quotation"""
    try:
        items = CustomerQuotationCRUD.get_quotation_items_by_quotation(db, quotation_id)
        return items
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )

@router.get("/quotation-items/{item_id}", response_model=QuotationItemResponse)
def get_quotation_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific quotation item by ID"""
    try:
        item = CustomerQuotationCRUD.get_quotation_item_by_id(db, item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quotation item not found"
            )
        return item
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )

@router.put("/quotation-items/{item_id}", response_model=QuotationItemResponse)
def update_quotation_item(
    item_id: int,
    item_data: QuotationItemUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a quotation item"""
    try:
        item = CustomerQuotationCRUD.update_quotation_item(db, item_id, item_data, updated_by=current_user.username)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quotation item not found"
            )
        return item
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )

@router.delete("/quotation-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quotation_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a quotation item (soft delete)"""
    try:
        success = CustomerQuotationCRUD.delete_quotation_item(db, item_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quotation item not found"
            )
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )

# ============================================================================
# QUOTATION ITEM ATTRIBUTE ENDPOINTS
# ============================================================================

@router.post("/quotation-item-attributes", response_model=QuotationItemAttributeResponse, status_code=status.HTTP_201_CREATED)
def create_quotation_item_attribute(
    attribute_data: QuotationItemAttributeCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new quotation item attribute"""
    try:
        attribute = CustomerQuotationCRUD.create_quotation_item_attribute(db, attribute_data, created_by=current_user.username)
        return attribute
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )

@router.get("/quotation-item-attributes", response_model=List[QuotationItemAttributeResponse])
def get_quotation_item_attributes(
    quotation_item_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all attributes for a specific quotation item"""
    try:
        attributes = CustomerQuotationCRUD.get_quotation_item_attributes_by_item(db, quotation_item_id)
        return attributes
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )

@router.get("/quotation-item-attributes/{attribute_id}", response_model=QuotationItemAttributeResponse)
def get_quotation_item_attribute(
    attribute_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific quotation item attribute by ID"""
    try:
        attribute = CustomerQuotationCRUD.get_quotation_item_attribute_by_id(db, attribute_id)
        if not attribute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quotation item attribute not found"
            )
        return attribute
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )

@router.put("/quotation-item-attributes/{attribute_id}", response_model=QuotationItemAttributeResponse)
def update_quotation_item_attribute(
    attribute_id: int,
    attribute_data: QuotationItemAttributeUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a quotation item attribute"""
    try:
        attribute = CustomerQuotationCRUD.update_quotation_item_attribute(db, attribute_id, attribute_data, updated_by=current_user.username)
        if not attribute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quotation item attribute not found"
            )
        return attribute
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )

@router.delete("/quotation-item-attributes/{attribute_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quotation_item_attribute(
    attribute_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a quotation item attribute (soft delete)"""
    try:
        success = CustomerQuotationCRUD.delete_quotation_item_attribute(db, attribute_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quotation item attribute not found"
            )
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )
