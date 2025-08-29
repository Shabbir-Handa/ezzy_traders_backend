"""
Employee Management CRUD Operations
Simplified employee management without complex role-permission systems
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

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
        db.commit()
        return employee

    @staticmethod
    def get_employee_by_id(db: Session, employee_id: int) -> Optional[EmployeeResponse]:
        return db.query(Employee).filter(Employee.id == employee_id).first()

    @staticmethod
    def get_all_employees(db: Session, skip: int = 0, limit: int = 100) -> List[EmployeeResponse]:
        return db.query(Employee).offset(skip).limit(limit).all()

    @staticmethod
    def get_active_employees(db: Session) -> List[EmployeeResponse]:
        return db.query(Employee).filter(Employee.is_active == True).all()

    @staticmethod
    def update_employee(db: Session, employee_id: int, data: EmployeeUpdate, username: str = None) -> Optional[EmployeeResponse]:
        employee = db.get(Employee, employee_id)
        if not employee:
            return None

        update_data = data.dict(exclude_unset=True)
        
        # Handle password hashing if password is being updated
        if 'password' in update_data:
            update_data['hashed_password'] = get_password_hash(update_data.pop('password'))
        
        for key, value in update_data.items():
            setattr(employee, key, value)
        
        employee.updated_by = username
        employee.updated_at = datetime.now(timezone.utc)

        db.commit()
        return employee

    @staticmethod
    def delete_employee(db: Session, employee_id: int) -> bool:
        employee = db.get(Employee, employee_id)
        if not employee:
            return False
        
        # Soft delete - just mark as inactive
        employee.is_active = False
        db.commit()
        return True

    @staticmethod
    def authenticate_employee(db: Session, username: str, password: str) -> Optional[EmployeeResponse]:
        """Authenticate an employee by username and password"""
        employee = db.query(Employee).filter(Employee.username == username).first()
        if not employee:
            return None
        
        if not verify_password(password, employee.hashed_password):
            return None
        
        return employee

    @staticmethod
    def activate_employee(db: Session, employee_id: int, username: str = None) -> Optional[EmployeeResponse]:
        """Activate an employee account"""
        employee = db.get(Employee, employee_id)
        if not employee:
            return None
        
        employee.is_active = True
        employee.updated_by = username
        employee.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        return employee

    @staticmethod
    def deactivate_employee(db: Session, employee_id: int, username: str = None) -> Optional[EmployeeResponse]:
        """Deactivate an employee account"""
        employee = db.get(Employee, employee_id)
        if not employee:
            return None
        
        employee.is_active = False
        employee.updated_by = username
        employee.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        return employee

    @staticmethod
    def change_employee_role(db: Session, employee_id: int, new_role: str, username: str = None) -> Optional[EmployeeResponse]:
        """Change an employee's role"""
        employee = db.get(Employee, employee_id)
        if not employee:
            return None
        
        employee.role = new_role
        employee.updated_by = username
        employee.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        return employee

    @staticmethod
    def get_employee_count(db: Session, active_only: bool = True) -> int:
        """Get total count of employees"""
        query = db.query(Employee)
        if active_only:
            query = query.filter(Employee.is_active == True)
        return query.count()
