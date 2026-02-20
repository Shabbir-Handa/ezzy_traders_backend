"""
Customers API Endpoints
CRUD for: Customers
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import math

from app.core.security import get_current_user
from app.db.session import get_db
from app.services.customer_service import CustomerService
from app.schemas.customer import (
    CustomerCreate, CustomerUpdate, CustomerResponse, PaginatedCustomerResponse,
)

router = APIRouter(prefix="", tags=["Customers"])


@router.get("/customers", response_model=PaginatedCustomerResponse)
async def get_all_customers(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    total = CustomerService.count_customers(db)
    skip = (page - 1) * size
    customers = CustomerService.get_all_customers(db, skip=skip, limit=size)
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
    customer = CustomerService.get_customer_by_id(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return CustomerService.create_customer(db, data, current_user.username)


@router.patch("/customers/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    data: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = CustomerService.update_customer(db, customer_id, data, current_user.username)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    return result


@router.delete("/customers/{customer_id}")
async def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not CustomerService.delete_customer(db, customer_id):
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer deleted"}
