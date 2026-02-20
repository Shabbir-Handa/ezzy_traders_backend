"""
Customer Repository
Data access layer for Customer entities.
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerRepository:

    @staticmethod
    def create_customer(db: Session, data: CustomerCreate, username: str = None) -> Customer:
        customer = Customer(
            **data.model_dump(),
            created_by=username or "system",
            updated_by=username or "system",
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer

    @staticmethod
    def get_customer_by_id(db: Session, customer_id: int) -> Optional[Customer]:
        return db.query(Customer).filter(Customer.id == customer_id).first()

    @staticmethod
    def get_all_customers(db: Session, skip: int = 0, limit: int = 100) -> List[Customer]:
        return db.query(Customer).offset(skip).limit(limit).all()

    @staticmethod
    def count_customers(db: Session) -> int:
        return db.query(Customer).count()

    @staticmethod
    def update_customer(db: Session, customer_id: int, data: CustomerUpdate, username: str = None) -> Optional[Customer]:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(customer, key, value)
        if username:
            customer.updated_by = username
        db.commit()
        db.refresh(customer)
        return customer

    @staticmethod
    def delete_customer(db: Session, customer_id: int) -> bool:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return False
        db.delete(customer)
        db.commit()
        return True
