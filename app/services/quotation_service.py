"""
Quotation Service
Business logic layer for Quotation and QuotationItem operations.
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import Quotation, QuotationItem
from app.repositories.quotation_repo import QuotationRepository
from app.schemas.quotation import (
    QuotationCreate, QuotationUpdate,
    QuotationItemCreate, QuotationItemUpdate,
)


class QuotationService:

    # QUOTATION
    @staticmethod
    def create_quotation(db: Session, data: QuotationCreate, username: str = None) -> Quotation:
        return QuotationRepository.create_quotation(db, data, username)

    @staticmethod
    def get_quotation_by_id(db: Session, quotation_id: int) -> Optional[Quotation]:
        return QuotationRepository.get_quotation_by_id(db, quotation_id)

    @staticmethod
    def get_quotation_by_number(db: Session, quotation_number: str) -> Optional[Quotation]:
        return QuotationRepository.get_quotation_by_number(db, quotation_number)

    @staticmethod
    def get_quotations_by_customer(db: Session, customer_id: int) -> List[Quotation]:
        return QuotationRepository.get_quotations_by_customer(db, customer_id)

    @staticmethod
    def get_all_quotations(db: Session, skip: int = 0, limit: int = 100) -> List[Quotation]:
        return QuotationRepository.get_all_quotations(db, skip, limit)

    @staticmethod
    def count_quotations(db: Session) -> int:
        return QuotationRepository.count_quotations(db)

    @staticmethod
    def recalculate_quotation_costs(db: Session, quotation_id: int) -> Optional[Quotation]:
        return QuotationRepository.recalculate_quotation_costs(db, quotation_id)

    @staticmethod
    def update_quotation(db: Session, quotation_id: int, data: QuotationUpdate, updated_by: str = None) -> Optional[Quotation]:
        return QuotationRepository.update_quotation(db, quotation_id, data, updated_by)

    @staticmethod
    def delete_quotation(db: Session, quotation_id: int) -> bool:
        return QuotationRepository.delete_quotation(db, quotation_id)

    # QUOTATION ITEM
    @staticmethod
    def create_quotation_item(db: Session, data: QuotationItemCreate, created_by: str = None) -> QuotationItem:
        return QuotationRepository.create_quotation_item(db, data, created_by)

    @staticmethod
    def get_quotation_item_by_id(db: Session, item_id: int) -> Optional[QuotationItem]:
        return QuotationRepository.get_quotation_item_by_id(db, item_id)

    @staticmethod
    def get_quotation_items_by_quotation(db: Session, quotation_id: int) -> List[QuotationItem]:
        return QuotationRepository.get_quotation_items_by_quotation(db, quotation_id)

    @staticmethod
    def update_quotation_item(db: Session, item_id: int, data: QuotationItemUpdate, updated_by: str = None) -> Optional[QuotationItem]:
        return QuotationRepository.update_quotation_item(db, item_id, data, updated_by)

    @staticmethod
    def delete_quotation_item(db: Session, item_id: int) -> bool:
        return QuotationRepository.delete_quotation_item(db, item_id)
