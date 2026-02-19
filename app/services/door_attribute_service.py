"""
Door Attribute Service
Business logic layer for DoorType, Attribute, NestedAttribute, and Unit operations.
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import (
    DoorType, Attribute, DoorTypeAttribute, AttributeOption,
    NestedAttribute, Unit, DoorTypeThicknessOption, NestedAttributeChild
)
from app.repositories.door_attribute_repo import DoorAttributeRepository
from app.schemas.door_type import (
    DoorTypeCreate, DoorTypeUpdate,
    DoorTypeThicknessOptionCreate, DoorTypeThicknessOptionUpdate,
    DoorTypeAttributeCreate, DoorTypeAttributeUpdate,
)
from app.schemas.attribute import (
    AttributeCreate, AttributeUpdate,
    AttributeOptionCreate, AttributeOptionUpdate,
    NestedAttributeCreate, NestedAttributeUpdate,
    NestedAttributeChildCreate, NestedAttributeChildUpdate,
)
from app.schemas.unit import UnitCreate, UnitUpdate


class DoorAttributeService:
    # ============================================================================
    # DOOR TYPE METHODS
    # ============================================================================

    @staticmethod
    def create_door_type(db: Session, data: DoorTypeCreate, username: str = None) -> DoorType:
        return DoorAttributeRepository.create_door_type(db, data, username)

    @staticmethod
    def get_door_type_by_id(db: Session, door_type_id: int) -> Optional[DoorType]:
        return DoorAttributeRepository.get_door_type_by_id(db, door_type_id)

    @staticmethod
    def get_all_door_types(db: Session, skip: int = 0, limit: int = 100) -> List[DoorType]:
        return DoorAttributeRepository.get_all_door_types(db, skip, limit)

    @staticmethod
    def count_door_types(db: Session) -> int:
        return DoorAttributeRepository.count_door_types(db)

    @staticmethod
    def update_door_type(db: Session, door_type_id: int, data: DoorTypeUpdate, username: str = None) -> Optional[DoorType]:
        return DoorAttributeRepository.update_door_type(db, door_type_id, data, username)

    @staticmethod
    def delete_door_type(db: Session, door_type_id: int) -> bool:
        return DoorAttributeRepository.delete_door_type(db, door_type_id)

    # ============================================================================
    # DOOR TYPE THICKNESS OPTION METHODS
    # ============================================================================

    @staticmethod
    def create_door_type_thickness_option(db: Session, data: DoorTypeThicknessOptionCreate, username: str = None) -> DoorTypeThicknessOption:
        return DoorAttributeRepository.create_door_type_thickness_option(db, data, username)

    @staticmethod
    def get_door_type_thickness_option_by_id(db: Session, thickness_option_id: int) -> Optional[DoorTypeThicknessOption]:
        return DoorAttributeRepository.get_door_type_thickness_option_by_id(db, thickness_option_id)

    @staticmethod
    def get_door_type_thickness_options_by_door_type(db: Session, door_type_id: int) -> List[DoorTypeThicknessOption]:
        return DoorAttributeRepository.get_door_type_thickness_options_by_door_type(db, door_type_id)

    @staticmethod
    def update_door_type_thickness_option(db: Session, thickness_option_id: int, data: DoorTypeThicknessOptionUpdate, username: str = None) -> Optional[DoorTypeThicknessOption]:
        return DoorAttributeRepository.update_door_type_thickness_option(db, thickness_option_id, data, username)

    @staticmethod
    def delete_door_type_thickness_option(db: Session, thickness_option_id: int) -> bool:
        return DoorAttributeRepository.delete_door_type_thickness_option(db, thickness_option_id)

    # ============================================================================
    # ATTRIBUTE METHODS
    # ============================================================================

    @staticmethod
    def create_attribute(db: Session, data: AttributeCreate, username: str = None) -> Attribute:
        return DoorAttributeRepository.create_attribute(db, data, username)

    @staticmethod
    def get_attribute_by_id(db: Session, attribute_id: int) -> Optional[Attribute]:
        return DoorAttributeRepository.get_attribute_by_id(db, attribute_id)

    @staticmethod
    def get_all_attributes(db: Session, skip: int = 0, limit: int = 100) -> List[Attribute]:
        return DoorAttributeRepository.get_all_attributes(db, skip, limit)

    @staticmethod
    def count_attributes(db: Session) -> int:
        return DoorAttributeRepository.count_attributes(db)

    @staticmethod
    def update_attribute(db: Session, attribute_id: int, data: AttributeUpdate, username: str = None) -> Optional[Attribute]:
        return DoorAttributeRepository.update_attribute(db, attribute_id, data, username)

    @staticmethod
    def delete_attribute(db: Session, attribute_id: int) -> bool:
        return DoorAttributeRepository.delete_attribute(db, attribute_id)

    # ============================================================================
    # DOOR TYPE ATTRIBUTE METHODS
    # ============================================================================

    @staticmethod
    def create_door_type_attribute(db: Session, data: DoorTypeAttributeCreate, username: str = None) -> DoorTypeAttribute:
        return DoorAttributeRepository.create_door_type_attribute(db, data, username)

    @staticmethod
    def get_door_type_attributes_by_door_type(db: Session, door_type_id: int) -> List[DoorTypeAttribute]:
        return DoorAttributeRepository.get_door_type_attributes_by_door_type(db, door_type_id)

    @staticmethod
    def get_door_type_attribute_by_id(db: Session, door_type_attribute_id: int) -> Optional[DoorTypeAttribute]:
        return DoorAttributeRepository.get_door_type_attribute_by_id(db, door_type_attribute_id)

    @staticmethod
    def update_door_type_attribute(db: Session, door_type_attribute_id: int, data: DoorTypeAttributeUpdate, username: str = None) -> Optional[DoorTypeAttribute]:
        return DoorAttributeRepository.update_door_type_attribute(db, door_type_attribute_id, data, username)

    @staticmethod
    def delete_door_type_attribute(db: Session, door_type_attribute_id: int) -> bool:
        return DoorAttributeRepository.delete_door_type_attribute(db, door_type_attribute_id)

    # ============================================================================
    # ATTRIBUTE OPTION METHODS
    # ============================================================================

    @staticmethod
    def create_attribute_option(db: Session, data: AttributeOptionCreate, username: str = None) -> AttributeOption:
        return DoorAttributeRepository.create_attribute_option(db, data, username)

    @staticmethod
    def get_attribute_options_by_attribute(db: Session, attribute_id: int) -> List[AttributeOption]:
        return DoorAttributeRepository.get_attribute_options_by_attribute(db, attribute_id)

    @staticmethod
    def get_attribute_option_by_id(db: Session, option_id: int) -> Optional[AttributeOption]:
        return DoorAttributeRepository.get_attribute_option_by_id(db, option_id)

    @staticmethod
    def update_attribute_option(db: Session, option_id: int, data: AttributeOptionUpdate, username: str = None) -> Optional[AttributeOption]:
        return DoorAttributeRepository.update_attribute_option(db, option_id, data, username)

    @staticmethod
    def delete_attribute_option(db: Session, option_id: int) -> bool:
        return DoorAttributeRepository.delete_attribute_option(db, option_id)

    # ============================================================================
    # NESTED ATTRIBUTE METHODS
    # ============================================================================

    @staticmethod
    def create_nested_attribute(db: Session, data: NestedAttributeCreate, username: str = None) -> NestedAttribute:
        return DoorAttributeRepository.create_nested_attribute(db, data, username)

    @staticmethod
    def get_all_nested_attributes(db: Session, skip: int = 0, limit: int = 100) -> List[NestedAttribute]:
        return DoorAttributeRepository.get_all_nested_attributes(db, skip, limit)

    @staticmethod
    def count_nested_attributes(db: Session) -> int:
        return DoorAttributeRepository.count_nested_attributes(db)

    @staticmethod
    def get_nested_attribute_by_id(db: Session, nested_attribute_id: int) -> Optional[NestedAttribute]:
        return DoorAttributeRepository.get_nested_attribute_by_id(db, nested_attribute_id)

    @staticmethod
    def update_nested_attribute(db: Session, nested_attribute_id: int, data: NestedAttributeUpdate, username: str = None) -> Optional[NestedAttribute]:
        return DoorAttributeRepository.update_nested_attribute(db, nested_attribute_id, data, username)

    @staticmethod
    def delete_nested_attribute(db: Session, nested_attribute_id: int) -> bool:
        return DoorAttributeRepository.delete_nested_attribute(db, nested_attribute_id)

    # ============================================================================
    # NESTED ATTRIBUTE CHILD METHODS
    # ============================================================================

    @staticmethod
    def create_nested_attribute_child(db: Session, data: NestedAttributeChildCreate, username: str = None) -> NestedAttributeChild:
        return DoorAttributeRepository.create_nested_attribute_child(db, data, username)

    @staticmethod
    def get_nested_attribute_children_by_nested_attribute(db: Session, nested_attribute_id: int) -> List[NestedAttributeChild]:
        return DoorAttributeRepository.get_nested_attribute_children_by_nested_attribute(db, nested_attribute_id)

    @staticmethod
    def get_nested_attribute_child_by_id(db: Session, nested_attribute_child_id: int) -> Optional[NestedAttributeChild]:
        return DoorAttributeRepository.get_nested_attribute_child_by_id(db, nested_attribute_child_id)

    @staticmethod
    def update_nested_attribute_child(db: Session, nested_attribute_child_id: int, data: NestedAttributeChildUpdate, username: str = None) -> Optional[NestedAttributeChild]:
        return DoorAttributeRepository.update_nested_attribute_child(db, nested_attribute_child_id, data, username)

    @staticmethod
    def delete_nested_attribute_child(db: Session, nested_attribute_child_id: int) -> bool:
        return DoorAttributeRepository.delete_nested_attribute_child(db, nested_attribute_child_id)

    # ============================================================================
    # UNIT METHODS
    # ============================================================================

    @staticmethod
    def create_unit(db: Session, data: UnitCreate, username: str = None) -> Unit:
        return DoorAttributeRepository.create_unit(db, data, username)

    @staticmethod
    def get_unit_by_id(db: Session, unit_id: int) -> Optional[Unit]:
        return DoorAttributeRepository.get_unit_by_id(db, unit_id)

    @staticmethod
    def get_all_units(db: Session, skip: int = 0, limit: int = 100) -> List[Unit]:
        return DoorAttributeRepository.get_all_units(db, skip, limit)

    @staticmethod
    def count_units(db: Session) -> int:
        return DoorAttributeRepository.count_units(db)

    @staticmethod
    def update_unit(db: Session, unit_id: int, data: UnitUpdate, username: str = None) -> Optional[Unit]:
        return DoorAttributeRepository.update_unit(db, unit_id, data, username)

    @staticmethod
    def delete_unit(db: Session, unit_id: int) -> bool:
        return DoorAttributeRepository.delete_unit(db, unit_id)
