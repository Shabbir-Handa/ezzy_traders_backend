"""
Employee Service
Business logic layer for Employee operations.
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.employee import Employee
from app.repositories.employee_repo import EmployeeRepository
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


class EmployeeService:

    @staticmethod
    def create_employee(db: Session, data: EmployeeCreate, username: str = None) -> Employee:
        return EmployeeRepository.create_employee(db, data, username)

    @staticmethod
    def get_employee_by_id(db: Session, employee_id: int) -> Optional[Employee]:
        return EmployeeRepository.get_employee_by_id(db, employee_id)

    @staticmethod
    def get_all_employees(db: Session, skip: int = 0, limit: int = 100) -> List[Employee]:
        return EmployeeRepository.get_all_employees(db, skip, limit)

    @staticmethod
    def get_employee_count(db: Session) -> int:
        return EmployeeRepository.get_employee_count(db)

    @staticmethod
    def update_employee(db: Session, employee_id: int, data: EmployeeUpdate, username: str = None) -> Optional[Employee]:
        return EmployeeRepository.update_employee(db, employee_id, data, username)

    @staticmethod
    def delete_employee(db: Session, employee_id: int) -> bool:
        return EmployeeRepository.delete_employee(db, employee_id)

    @staticmethod
    def authenticate_employee(db: Session, username: str, password: str) -> Optional[Employee]:
        return EmployeeRepository.authenticate_employee(db, username, password)

    @staticmethod
    def change_employee_password(db: Session, employee_id: int, new_password: str, username: str = None) -> Optional[Employee]:
        return EmployeeRepository.change_employee_password(db, employee_id, new_password, username)
