"""
Customer Quotation Service
Business logic layer for Customer and Quotation operations.
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import Customer, Quotation, QuotationItem, QuotationItemAttribute, QuotationItemNestedAttribute
from app.repositories.customer_quotation_repo import CustomerQuotationRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.schemas.quotation import (
    QuotationCreate, QuotationUpdate,
    QuotationItemCreate, QuotationItemUpdate,
    QuotationItemAttributeCreate, QuotationItemAttributeUpdate,
    QuotationItemNestedAttributeCreate
)


class CustomerQuotationService:
    # ============================================================================
    # CUSTOMER METHODS
    # ============================================================================

    @staticmethod
    def create_customer(db: Session, data: CustomerCreate, username: str = None) -> Customer:
        return CustomerQuotationRepository.create_customer(db, data, username)

    @staticmethod
    def get_customer_by_id(db: Session, customer_id: int) -> Optional[Customer]:
        return CustomerQuotationRepository.get_customer_by_id(db, customer_id)

    @staticmethod
    def get_all_customers(db: Session, skip: int = 0, limit: int = 100) -> List[Customer]:
        return CustomerQuotationRepository.get_all_customers(db, skip, limit)

    @staticmethod
    def count_customers(db: Session) -> int:
        return CustomerQuotationRepository.count_customers(db)

    @staticmethod
    def update_customer(db: Session, customer_id: int, data: CustomerUpdate, username: str = None) -> Optional[Customer]:
        return CustomerQuotationRepository.update_customer(db, customer_id, data, username)

    @staticmethod
    def delete_customer(db: Session, customer_id: int) -> bool:
        return CustomerQuotationRepository.delete_customer(db, customer_id)

    # ============================================================================
    # QUOTATION METHODS
    # ============================================================================

    @staticmethod
    def create_quotation(db: Session, data: QuotationCreate, username: str = None) -> Quotation:
        return CustomerQuotationRepository.create_quotation(db, data, username)

    @staticmethod
    def get_quotation_by_id(db: Session, quotation_id: int) -> Optional[Quotation]:
        return CustomerQuotationRepository.get_quotation_by_id(db, quotation_id)

    @staticmethod
    def get_quotation_by_number(db: Session, quotation_number: str) -> Optional[Quotation]:
        return CustomerQuotationRepository.get_quotation_by_number(db, quotation_number)

    @staticmethod
    def get_quotations_by_customer(db: Session, customer_id: int) -> List[Quotation]:
        return CustomerQuotationRepository.get_quotations_by_customer(db, customer_id)

    @staticmethod
    def get_all_quotations(db: Session, skip: int = 0, limit: int = 100) -> List[Quotation]:
        return CustomerQuotationRepository.get_all_quotations(db, skip, limit)

    @staticmethod
    def count_quotations(db: Session) -> int:
        return CustomerQuotationRepository.count_quotations(db)

    @staticmethod
    def recalculate_quotation_costs(db: Session, quotation_id: int) -> Optional[Quotation]:
        return CustomerQuotationRepository.recalculate_quotation_costs(db, quotation_id)

    @staticmethod
    def update_quotation(db: Session, quotation_id: int, data: QuotationUpdate, updated_by: str = None) -> Optional[Quotation]:
        return CustomerQuotationRepository.update_quotation(db, quotation_id, data, updated_by)

    @staticmethod
    def delete_quotation(db: Session, quotation_id: int) -> bool:
        return CustomerQuotationRepository.delete_quotation(db, quotation_id)

    # ============================================================================
    # QUOTATION ITEM METHODS
    # ============================================================================

    @staticmethod
    def create_quotation_item(db: Session, data: QuotationItemCreate, created_by: str = None) -> QuotationItem:
        return CustomerQuotationRepository.create_quotation_item(db, data, created_by)

    @staticmethod
    def get_quotation_item_by_id(db: Session, item_id: int) -> Optional[QuotationItem]:
        return CustomerQuotationRepository.get_quotation_item_by_id(db, item_id)

    @staticmethod
    def get_quotation_items_by_quotation(db: Session, quotation_id: int) -> List[QuotationItem]:
        return CustomerQuotationRepository.get_quotation_items_by_quotation(db, quotation_id)

    @staticmethod
    def update_quotation_item(db: Session, item_id: int, data: QuotationItemUpdate, updated_by: str = None) -> Optional[QuotationItem]:
        return CustomerQuotationRepository.update_quotation_item(db, item_id, data, updated_by)

    @staticmethod
    def delete_quotation_item(db: Session, item_id: int) -> bool:
        return CustomerQuotationRepository.delete_quotation_item(db, item_id)

    # ============================================================================
    # QUOTATION ITEM ATTRIBUTE METHODS
    # ============================================================================

    @staticmethod
    def create_quotation_item_attribute(db: Session, data: QuotationItemAttributeCreate, created_by: str = None) -> QuotationItemAttribute:
        return CustomerQuotationRepository.create_quotation_item_attribute(db, data, created_by)

    @staticmethod
    def get_quotation_item_attribute_by_id(db: Session, attribute_id: int) -> Optional[QuotationItemAttribute]:
        return CustomerQuotationRepository.get_quotation_item_attribute_by_id(db, attribute_id)

    @staticmethod
    def get_quotation_item_attributes_by_item(db: Session, quotation_item_id: int) -> List[QuotationItemAttribute]:
        return CustomerQuotationRepository.get_quotation_item_attributes_by_item(db, quotation_item_id)

    @staticmethod
    def update_quotation_item_attribute(db: Session, attribute_id: int, data: QuotationItemAttributeUpdate, updated_by: str = None) -> Optional[QuotationItemAttribute]:
        return CustomerQuotationRepository.update_quotation_item_attribute(db, attribute_id, data, updated_by)

    @staticmethod
    def delete_quotation_item_attribute(db: Session, attribute_id: int) -> bool:
        return CustomerQuotationRepository.delete_quotation_item_attribute(db, attribute_id)

    # ============================================================================
    # QUOTATION ITEM NESTED ATTRIBUTE METHODS
    # ============================================================================

    @staticmethod
    def create_quotation_item_nested_attribute(db: Session, data: QuotationItemNestedAttributeCreate, created_by: str = None) -> QuotationItemNestedAttribute:
        return CustomerQuotationRepository.create_quotation_item_nested_attribute(db, data, created_by)

    @staticmethod
    def get_quotation_item_nested_attribute_by_id(db: Session, nested_attribute_id: int) -> Optional[QuotationItemNestedAttribute]:
        return CustomerQuotationRepository.get_quotation_item_nested_attribute_by_id(db, nested_attribute_id)
