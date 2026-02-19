"""
Employee Management Endpoints
Routes contain NO business logic — all logic delegated to services.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.services.employee_service import EmployeeService
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse, PaginatedEmployeeResponse
from app.core.security import get_current_user
from app.db.session import get_db

router = APIRouter(prefix="/employees", tags=["Employee-Management"])


@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(
        employee_data: EmployeeCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Create a new employee"""
    try:
        employee = EmployeeService.create_employee(db, employee_data, current_user.username)
        db.commit()
        return employee
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.get("/", response_model=PaginatedEmployeeResponse)
def get_employees(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get all employees with pagination"""
    try:
        employees = EmployeeService.get_all_employees(db, skip=skip, limit=limit)
        total = EmployeeService.get_employee_count(db)

        return {
            "data": employees,
            "total": total,
            "page": (skip // limit) + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
        employee_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get a specific employee by ID"""
    try:
        employee = EmployeeService.get_employee_by_id(db, employee_id)
        if not employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
        return employee
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
        employee_id: int,
        employee_data: EmployeeUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Update an employee"""
    try:
        employee = EmployeeService.update_employee(db, employee_id, employee_data, current_user.username)
        if not employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
        db.commit()
        return employee
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(
        employee_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Delete an employee (soft delete)"""
    try:
        if employee_id == current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete your own account")

        success = EmployeeService.delete_employee(db, employee_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
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


@router.post("/{employee_id}/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_employee_password(
        employee_id: int,
        data: dict,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Change an employee's password"""
    try:
        new_password = data.get("password")
        EmployeeService.change_employee_password(db, employee_id, new_password, current_user.username)
        db.commit()
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")
