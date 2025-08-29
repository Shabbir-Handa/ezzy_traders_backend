"""
Employee Management Router
Simplified employee management without complex role-permission systems
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from db_helper.employee_crud import EmployeeCRUD
from schemas.schemas import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse
)
from dependencies import get_db, get_current_user

router = APIRouter(
    prefix="/api/employees",
    tags=["Employee-Management"],
)


# ============================================================================
# EMPLOYEE ENDPOINTS
# ============================================================================

@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(
        employee_data: EmployeeCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Create a new employee"""
    try:
        employee = EmployeeCRUD.create_employee(db, employee_data, current_user.username)
        return employee
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


@router.get("/", response_model=List[EmployeeResponse])
def get_employees(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        active_only: bool = Query(False),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get all employees with pagination"""
    try:
        if active_only:
            employees = EmployeeCRUD.get_active_employees(db)
        else:
            employees = EmployeeCRUD.get_all_employees(db, skip=skip, limit=limit)
        return employees
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


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
        employee_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get a specific employee by ID"""
    try:
        employee = EmployeeCRUD.get_employee_by_id(db, employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        return employee
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


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
        employee_id: int,
        employee_data: EmployeeUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Update an employee"""
    try:
        employee = EmployeeCRUD.update_employee(
            db, employee_id, employee_data, current_user.username
        )
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        return employee
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


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(
        employee_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Delete an employee (soft delete)"""
    try:
        # Prevent self-deletion
        if employee_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )

        success = EmployeeCRUD.delete_employee(db, employee_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
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


@router.get("/username/{username}", response_model=EmployeeResponse)
def get_employee_by_username(
        username: str,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get employee by username"""
    try:
        employee = EmployeeCRUD.get_employee_by_username(db, username)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        return employee
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


@router.get("/email/{email}", response_model=EmployeeResponse)
def get_employee_by_email(
        email: str,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get employee by email"""
    try:
        employee = EmployeeCRUD.get_employee_by_email(db, email)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        return employee
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


@router.patch("/{employee_id}/activate", response_model=EmployeeResponse)
def activate_employee(
        employee_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Activate an employee account"""
    try:
        employee = EmployeeCRUD.activate_employee(db, employee_id, current_user.username)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        return employee
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


@router.patch("/{employee_id}/deactivate", response_model=EmployeeResponse)
def deactivate_employee(
        employee_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Deactivate an employee account"""
    try:
        # Prevent self-deactivation
        if employee_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate your own account"
            )

        employee = EmployeeCRUD.deactivate_employee(db, employee_id, current_user.username)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        return employee
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
