"""
Employee Management CRUD Operations
Simplified employee management without complex role-permission systems
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from time_utils import now_ist
from fastapi import HTTPException, status
from db_helper.models import Employee
from schemas.schemas import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse
)
from dependencies import get_password_hash, verify_password


class EmployeeCRUD:
    # ============================================================================
    # EMPLOYEE METHODS
    # ============================================================================
    
    @staticmethod
    def create_employee(db: Session, data: EmployeeCreate, username: str = None) -> EmployeeResponse:
        hashed_password = get_password_hash(data.password)
        
        employee = Employee(
            **data.dict(exclude="password"),
            hashed_password=hashed_password,
            created_by=username,
            updated_by=username
        )
        db.add(employee)
        db.flush()
        return employee

    @staticmethod
    def get_employee_by_id(db: Session, employee_id: int) -> Optional[EmployeeResponse]:
        return db.query(Employee).filter(Employee.id == employee_id).first()

    @staticmethod
    def get_all_employees(db: Session, skip: int = 0, limit: int = 100) -> List[EmployeeResponse]:
        return db.query(Employee).offset(skip).limit(limit).all()

    @staticmethod
    def update_employee(db: Session, employee_id: int, data: EmployeeUpdate, username: str = None) -> Optional[EmployeeResponse]:
        employee = db.get(Employee, employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )

        update_data = data.dict(exclude_unset=True)
        
        # Handle password hashing if password is being updated
        if 'password' in update_data:
            update_data['hashed_password'] = get_password_hash(update_data.pop('password'))
        
        for key, value in update_data.items():
            setattr(employee, key, value)
        
        employee.updated_by = username
        employee.updated_at = now_ist()

        db.flush()
        return employee

    @staticmethod
    def delete_employee(db: Session, employee_id: int) -> bool:
        employee = db.get(Employee, employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        db.delete(employee)
        db.flush()
        return True

    @staticmethod
    def authenticate_employee(db: Session, username: str, password: str) -> Optional[EmployeeResponse]:
        """Authenticate an employee by username and password"""
        employee = db.query(Employee).filter(Employee.username == username).first()
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        if not verify_password(password, employee.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid password"
            )
        
        return employee

    @staticmethod
    def change_employee_role(db: Session, employee_id: int, new_role: str, username: str = None) -> Optional[EmployeeResponse]:
        """Change an employee's role"""
        employee = db.get(Employee, employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        employee.role = new_role
        employee.updated_by = username
        employee.updated_at = now_ist()
        
        db.flush()
        return employee

    @staticmethod
    def change_employee_password(db: Session, employee_id: int, new_password: str, username: str = None) -> Optional[EmployeeResponse]:
        """Change an employee's password"""
        employee = db.get(Employee, employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )

        if not new_password or len(new_password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long"
            )

        employee.hashed_password = get_password_hash(new_password)
        employee.updated_by = username
        employee.updated_at = now_ist()

        db.flush()
        return employee

    @staticmethod
    def get_employee_count(db: Session) -> int:
        return db.query(Employee).count()
