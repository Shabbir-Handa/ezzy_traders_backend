"""
Door and Attribute Management CRUD Operations
"""

from sqlalchemy.orm import Session, joinedload, selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import HTTPException, status

from db_helper.models import DoorType, Attribute, DoorTypeAttribute, AttributeOption, NestedAttribute, Unit, \
    DoorTypeThicknessOption, NestedAttributeChild
from schemas.schemas import (
    DoorTypeCreate, DoorTypeUpdate, DoorTypeResponse,
    AttributeCreate, AttributeUpdate, AttributeResponse,
    DoorTypeAttributeCreate, DoorTypeAttributeUpdate, DoorTypeAttributeResponse,
    AttributeOptionCreate, AttributeOptionUpdate, AttributeOptionResponse,
    NestedAttributeCreate, NestedAttributeUpdate, NestedAttributeResponse,
    UnitCreate, UnitUpdate, UnitResponse,
    DoorTypeThicknessOptionCreate, DoorTypeThicknessOptionUpdate, DoorTypeThicknessOptionResponse,
    NestedAttributeChildCreate, NestedAttributeChildUpdate, NestedAttributeChildResponse
)


class DoorAttributeCRUD:
    # ============================================================================
    # DOOR TYPE METHODS
    # ============================================================================

    @staticmethod
    def create_door_type(db: Session, data: DoorTypeCreate, username: str = None) -> DoorTypeResponse:
        door_type = DoorType(
            **data.dict(exclude="thickness_options"),
            created_by=username,
            updated_by=username
        )
        db.add(door_type)
        db.flush()
        if data.thickness_options:
            for thickness_option in data.thickness_options:
                thickness_option.door_type_id = door_type.id
                db_thickness_option = DoorTypeThicknessOption(
                    **thickness_option.dict(),
                    created_by=username,
                    updated_by=username
                )
                db.add(db_thickness_option)
        db.flush()
        return door_type

    @staticmethod
    def get_door_type_by_id(db: Session, door_type_id: int) -> Optional[DoorTypeResponse]:
        return db.query(DoorType).options(
            joinedload(DoorType.door_type_attributes).joinedload(DoorTypeAttribute.attribute).joinedload(Attribute.options),
            joinedload(DoorType.door_type_attributes).joinedload(DoorTypeAttribute.attribute).selectinload(Attribute.unit),
            joinedload(DoorType.door_type_attributes).joinedload(DoorTypeAttribute.nested_attributes).joinedload(NestedAttribute.nested_attribute_children).joinedload(NestedAttributeChild.attribute).joinedload(Attribute.options),
            joinedload(DoorType.door_type_attributes).joinedload(DoorTypeAttribute.nested_attributes).joinedload(NestedAttribute.nested_attribute_children).joinedload(NestedAttributeChild.attribute).selectinload(Attribute.unit),
            joinedload(DoorType.thickness_options)
        ).filter(DoorType.id == door_type_id).first()

    @staticmethod
    def get_all_door_types(db: Session, skip: int = 0, limit: int = 100) -> List[DoorTypeResponse]:
        return db.query(DoorType).options(
            selectinload(DoorType.door_type_attributes).joinedload(DoorTypeAttribute.attribute).joinedload(Attribute.options),
            selectinload(DoorType.door_type_attributes).joinedload(DoorTypeAttribute.attribute).selectinload(Attribute.unit),
            selectinload(DoorType.door_type_attributes).joinedload(DoorTypeAttribute.nested_attributes).joinedload(NestedAttribute.nested_attribute_children).joinedload(NestedAttributeChild.attribute).joinedload(Attribute.options),
            selectinload(DoorType.door_type_attributes).joinedload(DoorTypeAttribute.nested_attributes).joinedload(NestedAttribute.nested_attribute_children).joinedload(NestedAttributeChild.attribute).selectinload(Attribute.unit),
            joinedload(DoorType.thickness_options)
        ).offset(skip).limit(limit).all()

    @staticmethod
    def count_door_types(db: Session) -> int:
        return db.query(DoorType).count()

    @staticmethod
    def update_door_type(db: Session, door_type_id: int, data: DoorTypeUpdate, username: str = None) -> Optional[
        DoorTypeResponse]:
        door_type = db.get(DoorType, door_type_id)
        if not door_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Door type not found"
            )

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(door_type, key, value)

        door_type.updated_by = username
        door_type.updated_at = datetime.now(timezone.utc)

        db.flush()
        return door_type

    @staticmethod
    def delete_door_type(db: Session, door_type_id: int) -> bool:
        door_type = db.get(DoorType, door_type_id)
        if not door_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Door type not found"
            )
        if not door_type.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Door type is associated with quotation items"
            )
        db.delete(door_type)
        db.flush()
        return True


    # ============================================================================
    # DOOR TYPE THICKNESS OPTION METHODS
    # ============================================================================

    @staticmethod
    def create_door_type_thickness_option(db: Session, data: DoorTypeThicknessOptionCreate, username: str = None) -> DoorTypeThicknessOptionResponse:
        thickness_option = DoorTypeThicknessOption(
            **data.dict(),
            created_by=username,
            updated_by=username
        )
        db.add(thickness_option)
        db.flush()
        return thickness_option

    @staticmethod
    def get_door_type_thickness_option_by_id(db: Session, thickness_option_id: int) -> Optional[DoorTypeThicknessOptionResponse]:
        return db.query(DoorTypeThicknessOption).filter(DoorTypeThicknessOption.id == thickness_option_id).first()

    @staticmethod
    def get_door_type_thickness_options_by_door_type(db: Session, door_type_id: int) -> List[DoorTypeThicknessOptionResponse]:
        return db.query(DoorTypeThicknessOption).filter(
            DoorTypeThicknessOption.door_type_id == door_type_id
        ).order_by(DoorTypeThicknessOption.thickness_value).all()

    @staticmethod
    def update_door_type_thickness_option(db: Session, thickness_option_id: int, data: DoorTypeThicknessOptionUpdate, username: str = None) -> Optional[DoorTypeThicknessOptionResponse]:
        thickness_option = db.get(DoorTypeThicknessOption, thickness_option_id)
        if not thickness_option:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Door type thickness option not found"
            )

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(thickness_option, key, value)

        thickness_option.updated_by = username
        thickness_option.updated_at = datetime.now(timezone.utc)

        db.flush()
        return thickness_option

    @staticmethod
    def delete_door_type_thickness_option(db: Session, thickness_option_id: int) -> bool:
        thickness_option = db.get(DoorTypeThicknessOption, thickness_option_id)
        if not thickness_option:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Door type thickness option not found"
            )

        if thickness_option.quotation_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Door type thickness option is associated with quotation items"
            )
        db.delete(thickness_option)
        db.flush()
        return True

    # ============================================================================
    # ATTRIBUTE METHODS
    # ============================================================================

    @staticmethod
    def create_attribute(db: Session, data: AttributeCreate, username: str = None) -> AttributeResponse:
        if not data.has_options and data.cost_type in ["constant", "variable"]:
            if not data.cost:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cost is required for constant and variable cost types"
                )
        if data.cost_type == "variable" and not data.unit_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unit is required for variable cost type"
            )
        if data.cost_type != "variable" and data.unit_id:
            data.unit_id = None
        if data.has_options and data.cost_type in ["constant", "variable"]:
            if data.cost:
                data.cost = None
        attribute = Attribute(
            **data.dict(exclude={"options", "has_options"}),
            created_by=username,
            updated_by=username
        )
        db.add(attribute)
        db.flush()
        if data.options:
            for option in data.options:
                option.attribute_id = attribute.id
                db_option = AttributeOption(
                    **option.dict(),
                    attribute_id=attribute.id,
                    created_by=username,
                    updated_by=username
                )
                db.add(db_option)
        db.flush()
        return attribute

    @staticmethod
    def get_attribute_by_id(db: Session, attribute_id: int) -> Optional[AttributeResponse]:
        return db.query(Attribute).options(
            joinedload(Attribute.options).joinedload(AttributeOption.unit),
            joinedload(Attribute.unit)
        ).filter(Attribute.id == attribute_id).first()

    @staticmethod
    def get_all_attributes(db: Session, skip: int = 0, limit: int = 100) -> List[AttributeResponse]:
        query = db.query(Attribute).options(
            joinedload(Attribute.options).joinedload(AttributeOption.unit),
            joinedload(Attribute.unit)
        )
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count_attributes(db: Session) -> int:
        return db.query(Attribute).count()

    @staticmethod
    def update_attribute(db: Session, attribute_id: int, data: AttributeUpdate, username: str = None) -> Optional[
        AttributeResponse]:
        attribute = db.get(Attribute, attribute_id)
        if not attribute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attribute not found"
            )

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(attribute, key, value)

        attribute.updated_by = username
        attribute.updated_at = datetime.now(timezone.utc)

        db.flush()
        return attribute

    @staticmethod
    def delete_attribute(db: Session, attribute_id: int) -> bool:
        attribute = db.get(Attribute, attribute_id)
        if not attribute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attribute not found"
            )

        if attribute.quotation_item_attribute:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attribute is associated with quotation item attribute"
            )

        db.delete(attribute)
        db.flush()
        return True

    # ============================================================================
    # DOOR TYPE ATTRIBUTE METHODS
    # ============================================================================

    @staticmethod
    def create_door_type_attribute(db: Session, data: DoorTypeAttributeCreate,
                                username: str = None) -> DoorTypeAttributeResponse:
        door_type_attribute = DoorTypeAttribute(
            **data.dict(),
            created_by=username,
            updated_by=username
        )
        db.add(door_type_attribute)
        db.flush()
        return door_type_attribute

    @staticmethod
    def get_door_type_attributes_by_door_type(db: Session, door_type_id: int) -> List[DoorTypeAttributeResponse]:
        return db.query(DoorTypeAttribute).options(
            joinedload(DoorTypeAttribute.attribute).selectinload(Attribute.unit),
            joinedload(DoorTypeAttribute.attribute).joinedload(Attribute.options),
            joinedload(DoorTypeAttribute.nested_attribute).joinedload(NestedAttribute.nested_attribute_children).selectinload(Attribute.unit),
            joinedload(DoorTypeAttribute.nested_attribute).joinedload(NestedAttribute.nested_attribute_children).joinedload(Attribute.options),
        ).filter(
            DoorTypeAttribute.door_type_id == door_type_id
        ).order_by(DoorTypeAttribute.order).all()

    @staticmethod
    def get_door_type_attribute_by_id(db: Session, door_type_attribute_id: int) -> Optional[DoorTypeAttributeResponse]:
        return db.query(DoorTypeAttribute).options(
            joinedload(DoorTypeAttribute.attribute).selectinload(Attribute.unit),
            joinedload(DoorTypeAttribute.attribute).joinedload(Attribute.options),
            joinedload(DoorTypeAttribute.nested_attribute).joinedload(NestedAttribute.nested_attribute_children).selectinload(Attribute.unit),
            joinedload(DoorTypeAttribute.nested_attribute).joinedload(NestedAttribute.nested_attribute_children).joinedload(Attribute.options),
        ).filter(DoorTypeAttribute.id == door_type_attribute_id).first()

    @staticmethod
    def update_door_type_attribute(db: Session, door_type_attribute_id: int, data: DoorTypeAttributeUpdate,
                                username: str = None) -> Optional[DoorTypeAttributeResponse]:
        door_type_attribute = db.get(DoorTypeAttribute, door_type_attribute_id)
        if not door_type_attribute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Door type attribute not found"
            )

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(door_type_attribute, key, value)

        door_type_attribute.updated_by = username
        door_type_attribute.updated_at = datetime.now(timezone.utc)

        db.flush()
        return door_type_attribute

    @staticmethod
    def delete_door_type_attribute(db: Session, door_type_attribute_id: int) -> bool:
        door_type_attribute = db.get(DoorTypeAttribute, door_type_attribute_id)
        if not door_type_attribute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Door type attribute not found"
            )
        if not door_type_attribute.nested_attribute:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Door type attribute is associated with nested attribute"
            )

        db.delete(door_type_attribute)
        db.flush()
        return True

    # ============================================================================
    # ATTRIBUTE OPTION METHODS
    # ============================================================================

    @staticmethod
    def create_attribute_option(db: Session, data: AttributeOptionCreate,
                                username: str = None) -> AttributeOptionResponse:
        attribute_option = AttributeOption(
            **data.dict(),
            created_by=username,
            updated_by=username
        )
        db.add(attribute_option)
        db.flush()
        return attribute_option

    @staticmethod
    def get_attribute_options_by_attribute(db: Session, attribute_id: int) -> List[AttributeOptionResponse]:
        return db.query(AttributeOption).filter(
            AttributeOption.attribute_id == attribute_id
        ).all()

    @staticmethod
    def get_attribute_option_by_id(db: Session, option_id: int) -> Optional[AttributeOptionResponse]:
        return db.query(AttributeOption).filter(AttributeOption.id == option_id).first()

    @staticmethod
    def update_attribute_option(db: Session, option_id: int, data: AttributeOptionUpdate, username: str = None) -> \
    Optional[AttributeOptionResponse]:
        attribute_option = db.get(AttributeOption, option_id)
        if not attribute_option:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attribute option not found"
            )

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(attribute_option, key, value)

        attribute_option.updated_by = username
        attribute_option.updated_at = datetime.now(timezone.utc)

        db.flush()
        return attribute_option

    @staticmethod
    def delete_attribute_option(db: Session, option_id: int) -> bool:
        attribute_option = db.get(AttributeOption, option_id)
        if not attribute_option:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attribute option not found"
            )

        if not attribute_option.quotation_item_attribute:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attribute option is associated with quotation item attribute"
            )

        db.delete(attribute_option)
        db.flush()
        return True

    # ============================================================================
    # NESTED ATTRIBUTE METHODS
    # ============================================================================

    @staticmethod
    def create_nested_attribute(db: Session, data: NestedAttributeCreate,
                                username: str = None) -> NestedAttributeResponse:
        nested_attribute = NestedAttribute(
            **data.dict(exclude="children"),
            created_by=username,
            updated_by=username
        )
        db.add(nested_attribute)
        db.flush()
        if data.children:
            for child in data.children:
                if not db.get(Attribute, child.attribute_id):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Attribute with id {child.attribute_id} not found"
                    )
                child.nested_attribute_id = nested_attribute.id
                db_child = NestedAttributeChild(
                    **child.dict(),
                    created_by=username,
                    updated_by=username
                )
                db.add(db_child)
        db.flush()
        return nested_attribute

    @staticmethod
    def get_all_nested_attributes(db: Session, skip: int = 0, limit: int = 100) -> List[NestedAttributeResponse]:
        return db.query(NestedAttribute).options(
            joinedload(NestedAttribute.nested_attribute_children).joinedload(NestedAttributeChild.attribute).selectinload(Attribute.unit),
            joinedload(NestedAttribute.nested_attribute_children).joinedload(NestedAttributeChild.attribute).joinedload(Attribute.options)
        ).offset(skip).limit(limit).all()

    @staticmethod
    def count_nested_attributes(db: Session) -> int:
        return db.query(NestedAttribute).count()

    @staticmethod
    def get_nested_attribute_by_id(db: Session, nested_attribute_id: int) -> Optional[NestedAttributeResponse]:
        return db.query(NestedAttribute).options(
            joinedload(NestedAttribute.nested_attribute_children).joinedload(NestedAttributeChild.attribute).selectinload(Attribute.unit),
            joinedload(NestedAttribute.nested_attribute_children).joinedload(NestedAttributeChild.attribute).joinedload(Attribute.options)
        ).filter(NestedAttribute.id == nested_attribute_id).first()

    @staticmethod
    def update_nested_attribute(db: Session, nested_attribute_id: int, data: NestedAttributeUpdate,
                                username: str = None) -> Optional[NestedAttributeResponse]:
        nested_attribute = db.get(NestedAttribute, nested_attribute_id)
        if not nested_attribute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nested attribute not found"
            )

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(nested_attribute, key, value)

        nested_attribute.updated_by = username
        nested_attribute.updated_at = datetime.now(timezone.utc)

        db.flush()
        return nested_attribute

    @staticmethod
    def delete_nested_attribute(db: Session, nested_attribute_id: int) -> bool:
        nested_attribute = db.get(NestedAttribute, nested_attribute_id)
        if not nested_attribute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nested attribute not found"
            )

        if not nested_attribute.quotation_item_nested_attribute:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nested attribute is associated with quotation item nested attribute"
            )

        db.delete(nested_attribute)
        db.flush()
        return True

    # ============================================================================
    # NESTED ATTRIBUTE CHILD METHODS
    # ============================================================================

    @staticmethod
    def create_nested_attribute_child(db: Session, data: NestedAttributeChildCreate,
                                username: str = None) -> NestedAttributeChildResponse:
        nested_attribute_child = NestedAttributeChild(
            **data.dict(),
            created_by=username,
            updated_by=username
        )
        db.add(nested_attribute_child)
        db.flush()
        return nested_attribute_child

    @staticmethod
    def get_nested_attribute_children_by_nested_attribute(db: Session, nested_attribute_id: int) -> List[NestedAttributeChildResponse]:
        return db.query(NestedAttributeChild).options(
            joinedload(NestedAttributeChild.attribute).selectinload(Attribute.unit),
            joinedload(NestedAttributeChild.attribute).joinedload(Attribute.options)
        ).filter(NestedAttributeChild.nested_attribute_id == nested_attribute_id).all()

    @staticmethod
    def get_nested_attribute_child_by_id(db: Session, nested_attribute_child_id: int) -> Optional[NestedAttributeChildResponse]:
        return db.query(NestedAttributeChild).options(
            joinedload(NestedAttributeChild.attribute).selectinload(Attribute.unit),
            joinedload(NestedAttributeChild.attribute).joinedload(Attribute.options)
        ).filter(NestedAttributeChild.id == nested_attribute_child_id).first()

    @staticmethod
    def update_nested_attribute_child(db: Session, nested_attribute_child_id: int, data: NestedAttributeChildUpdate, username: str = None) -> Optional[NestedAttributeChildResponse]:
        nested_attribute_child = db.get(NestedAttributeChild, nested_attribute_child_id)
        if not nested_attribute_child:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nested attribute child not found"
            )

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(nested_attribute_child, key, value)

        nested_attribute_child.updated_by = username
        nested_attribute_child.updated_at = datetime.now(timezone.utc)

        db.flush()
        return nested_attribute_child

    @staticmethod
    def delete_nested_attribute_child(db: Session, nested_attribute_child_id: int) -> bool:
        nested_attribute_child = db.get(NestedAttributeChild, nested_attribute_child_id)
        if not nested_attribute_child:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nested attribute child not found"
            )

        db.delete(nested_attribute_child)
        db.flush()
        return True

    # ============================================================================
    # UNIT METHODS
    # ============================================================================

    @staticmethod
    def create_unit(db: Session, data: UnitCreate, username: str = None) -> UnitResponse:
        unit = Unit(
            **data.dict(),
            created_by=username,
            updated_by=username
        )
        db.add(unit)
        db.flush()
        return unit

    @staticmethod
    def get_unit_by_id(db: Session, unit_id: int) -> Optional[UnitResponse]:
        return db.query(Unit).filter(Unit.id == unit_id).first()

    @staticmethod
    def get_all_units(db: Session, skip: int = 0, limit: int = 100) -> List[UnitResponse]:
        return db.query(Unit).offset(skip).limit(limit).all()

    @staticmethod
    def count_units(db: Session) -> int:
        return db.query(Unit).count()

    @staticmethod
    def update_unit(db: Session, unit_id: int, data: UnitUpdate, username: str = None) -> Optional[UnitResponse]:
        unit = db.get(Unit, unit_id)
        if not unit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unit not found"
            )

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(unit, key, value)

        unit.updated_by = username
        unit.updated_at = datetime.now(timezone.utc)

        db.flush()
        return unit

    @staticmethod
    def delete_unit(db: Session, unit_id: int) -> bool:
        unit = db.get(Unit, unit_id)
        if not unit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unit not found"
            )

        if unit.attributes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unit is associated with attributes"
            )

        db.delete(unit)
        db.flush()
        return True
        