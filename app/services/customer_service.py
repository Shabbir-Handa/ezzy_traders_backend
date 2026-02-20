"""
Customer Service
Business logic layer for Customer operations.
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import Customer
from app.repositories.customer_repo import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerService:

    @staticmethod
    def create_customer(db: Session, data: CustomerCreate, username: str = None) -> Customer:
        return CustomerRepository.create_customer(db, data, username)

    @staticmethod
    def get_customer_by_id(db: Session, customer_id: int) -> Optional[Customer]:
        return CustomerRepository.get_customer_by_id(db, customer_id)

    @staticmethod
    def get_all_customers(db: Session, skip: int = 0, limit: int = 100) -> List[Customer]:
        return CustomerRepository.get_all_customers(db, skip, limit)

    @staticmethod
    def count_customers(db: Session) -> int:
        return CustomerRepository.count_customers(db)

    @staticmethod
    def update_customer(db: Session, customer_id: int, data: CustomerUpdate, username: str = None) -> Optional[Customer]:
        return CustomerRepository.update_customer(db, customer_id, data, username)

    @staticmethod
    def delete_customer(db: Session, customer_id: int) -> bool:
        return CustomerRepository.delete_customer(db, customer_id)
