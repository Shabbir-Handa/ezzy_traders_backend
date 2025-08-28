"""
Door and Attribute Management CRUD Operations
"""

from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from db_helper.models import DoorType, Attribute, EntityAttribute, AttributeOption, NestedAttribute, Unit
from schemas.schemas import (
    DoorTypeCreate, DoorTypeUpdate, DoorTypeResponse,
    AttributeCreate, AttributeUpdate, AttributeResponse,
    EntityAttributeCreate, EntityAttributeUpdate, EntityAttributeResponse,
    AttributeOptionCreate, AttributeOptionUpdate, AttributeOptionResponse,
    NestedAttributeCreate, NestedAttributeUpdate, NestedAttributeResponse,
    UnitCreate, UnitUpdate, UnitResponse
)


class DoorAttributeCRUD:
    # ============================================================================
    # DOOR TYPE METHODS
    # ============================================================================
    
    @staticmethod
    def create_door_type(db: Session, data: DoorTypeCreate, created_by: str = None) -> DoorTypeResponse:
        door_type = DoorType(
            name=data.name,
            description=data.description,
            base_price=data.base_price,
            is_active=data.is_active,
            created_by=created_by
        )
        db.add(door_type)
        db.commit()
        db.refresh(door_type)
        return door_type

    @staticmethod
    def get_door_type_by_id(db: Session, door_type_id: int) -> Optional[DoorType]:
        return db.query(DoorType).options(
            joinedload(DoorType.attributes).joinedload(EntityAttribute.attribute),
            joinedload(DoorType.thickness_options)
        ).filter(DoorType.id == door_type_id).first()

    @staticmethod
    def get_door_type_by_name(db: Session, name: str) -> Optional[DoorType]:
        return db.query(DoorType).filter(DoorType.name == name).first()

    @staticmethod
    def get_all_door_types(db: Session, skip: int = 0, limit: int = 100) -> List[DoorType]:
        return db.query(DoorType).options(
            joinedload(DoorType.attributes).joinedload(EntityAttribute.attribute),
            joinedload(DoorType.thickness_options)
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_active_door_types(db: Session) -> List[DoorType]:
        return db.query(DoorType).options(
            joinedload(DoorType.attributes).joinedload(EntityAttribute.attribute),
            joinedload(DoorType.thickness_options)
        ).filter(DoorType.is_active == True).all()

    @staticmethod
    def update_door_type(db: Session, door_type_id: int, data: DoorTypeUpdate, updated_by: str = None) -> Optional[DoorType]:
        door_type = db.get(DoorType, door_type_id)
        if not door_type:
            return None

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(door_type, key, value)
        
        door_type.updated_by = updated_by
        door_type.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(door_type)
        return door_type

    @staticmethod
    def delete_door_type(db: Session, door_type_id: int) -> bool:
        door_type = db.get(DoorType, door_type_id)
        if not door_type:
            return False
        
        # Soft delete - just mark as inactive
        door_type.is_active = False
        db.commit()
        return True

    # ============================================================================
    # ATTRIBUTE METHODS
    # ============================================================================
    
    @staticmethod
    def create_attribute(db: Session, data: AttributeCreate, created_by: str = None) -> AttributeResponse:
        attribute = Attribute(
            name=data.name,
            description=data.description,
            double_side=data.double_side,
            cost_type=data.cost_type,
            fixed_cost=data.fixed_cost,
            cost_per_unit=data.cost_per_unit,
            unit_id=data.unit_id,
            domain=data.domain,
            is_active=data.is_active,
            created_by=created_by
        )
        db.add(attribute)
        db.commit()
        db.refresh(attribute)
        return attribute

    @staticmethod
    def get_attribute_by_id(db: Session, attribute_id: int) -> Optional[Attribute]:
        return db.query(Attribute).options(
            joinedload(Attribute.options),
            joinedload(Attribute.unit)
        ).filter(Attribute.id == attribute_id).first()

    @staticmethod
    def get_attribute_by_name(db: Session, name: str) -> Optional[Attribute]:
        return db.query(Attribute).filter(Attribute.name == name).first()

    @staticmethod
    def get_attributes_by_domain(db: Session, domain: str) -> List[Attribute]:
        return db.query(Attribute).options(
            joinedload(Attribute.options),
            joinedload(Attribute.unit)
        ).filter(Attribute.domain == domain, Attribute.is_active == True).all()

    @staticmethod
    def get_all_attributes(db: Session, skip: int = 0, limit: int = 100) -> List[Attribute]:
        return db.query(Attribute).options(
            joinedload(Attribute.options),
            joinedload(Attribute.unit)
        ).offset(skip).limit(limit).all()

    @staticmethod
    def update_attribute(db: Session, attribute_id: int, data: AttributeUpdate, updated_by: str = None) -> Optional[Attribute]:
        attribute = db.get(Attribute, attribute_id)
        if not attribute:
            return None

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(attribute, key, value)
        
        attribute.updated_by = updated_by
        attribute.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(attribute)
        return attribute

    @staticmethod
    def delete_attribute(db: Session, attribute_id: int) -> bool:
        attribute = db.get(Attribute, attribute_id)
        if not attribute:
            return False
        
        # Soft delete - just mark as inactive
        attribute.is_active = False
        db.commit()
        return True

    # ============================================================================
    # ENTITY ATTRIBUTE METHODS
    # ============================================================================
    
    @staticmethod
    def create_entity_attribute(db: Session, data: EntityAttributeCreate, created_by: str = None) -> EntityAttributeResponse:
        entity_attribute = EntityAttribute(
            entity_type=data.entity_type,
            entity_id=data.entity_id,
            attribute_id=data.attribute_id,
            required=data.required,
            order=data.order,
            custom_value=data.custom_value,
            is_active=data.is_active,
            created_by=created_by
        )
        db.add(entity_attribute)
        db.commit()
        db.refresh(entity_attribute)
        return entity_attribute

    @staticmethod
    def get_entity_attributes_by_entity(db: Session, entity_type: str, entity_id: int) -> List[EntityAttribute]:
        return db.query(EntityAttribute).options(
            joinedload(EntityAttribute.attribute)
        ).filter(
            EntityAttribute.entity_type == entity_type,
            EntityAttribute.entity_id == entity_id,
            EntityAttribute.is_active == True
        ).order_by(EntityAttribute.order).all()

    @staticmethod
    def get_entity_attribute_by_id(db: Session, entity_attribute_id: int) -> Optional[EntityAttribute]:
        return db.query(EntityAttribute).options(
            joinedload(EntityAttribute.attribute)
        ).filter(EntityAttribute.id == entity_attribute_id).first()

    @staticmethod
    def update_entity_attribute(db: Session, entity_attribute_id: int, data: EntityAttributeUpdate, updated_by: str = None) -> Optional[EntityAttribute]:
        entity_attribute = db.get(EntityAttribute, entity_attribute_id)
        if not entity_attribute:
            return None

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(entity_attribute, key, value)
        
        entity_attribute.updated_by = updated_by
        entity_attribute.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(entity_attribute)
        return entity_attribute

    @staticmethod
    def delete_entity_attribute(db: Session, entity_attribute_id: int) -> bool:
        entity_attribute = db.get(EntityAttribute, entity_attribute_id)
        if not entity_attribute:
            return False
        
        # Soft delete - just mark as inactive
        entity_attribute.is_active = False
        db.commit()
        return True

    # ============================================================================
    # ATTRIBUTE OPTION METHODS
    # ============================================================================
    
    @staticmethod
    def create_attribute_option(db: Session, data: AttributeOptionCreate, created_by: str = None) -> AttributeOptionResponse:
        attribute_option = AttributeOption(
            attribute_id=data.attribute_id,
            value=data.value,
            cost_adjustment=data.cost_adjustment,
            is_active=data.is_active,
            created_by=created_by
        )
        db.add(attribute_option)
        db.commit()
        db.refresh(attribute_option)
        return attribute_option

    @staticmethod
    def get_attribute_options_by_attribute(db: Session, attribute_id: int) -> List[AttributeOption]:
        return db.query(AttributeOption).filter(
            AttributeOption.attribute_id == attribute_id,
            AttributeOption.is_active == True
        ).all()

    @staticmethod
    def get_attribute_option_by_id(db: Session, option_id: int) -> Optional[AttributeOption]:
        return db.query(AttributeOption).filter(AttributeOption.id == option_id).first()

    @staticmethod
    def update_attribute_option(db: Session, option_id: int, data: AttributeOptionUpdate, updated_by: str = None) -> Optional[AttributeOption]:
        attribute_option = db.get(AttributeOption, option_id)
        if not attribute_option:
            return None

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(attribute_option, key, value)
        
        attribute_option.updated_by = updated_by
        attribute_option.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(attribute_option)
        return attribute_option

    @staticmethod
    def delete_attribute_option(db: Session, option_id: int) -> bool:
        attribute_option = db.get(AttributeOption, option_id)
        if not attribute_option:
            return False
        
        # Soft delete - just mark as inactive
        attribute_option.is_active = False
        db.commit()
        return True

    # ============================================================================
    # NESTED ATTRIBUTE METHODS
    # ============================================================================
    
    @staticmethod
    def create_nested_attribute(db: Session, data: NestedAttributeCreate, created_by: str = None) -> NestedAttributeResponse:
        nested_attribute = NestedAttribute(
            attribute_id=data.attribute_id,
            nested_attribute_id=data.nested_attribute_id,
            quantity=data.quantity,
            is_active=data.is_active,
            created_by=created_by
        )
        db.add(nested_attribute)
        db.commit()
        db.refresh(nested_attribute)
        return nested_attribute

    @staticmethod
    def get_nested_attributes_by_attribute(db: Session, attribute_id: int) -> List[NestedAttribute]:
        return db.query(NestedAttribute).options(
            joinedload(NestedAttribute.nested_attribute).joinedload(Attribute.options),
            joinedload(NestedAttribute.nested_attribute).joinedload(Attribute.unit)
        ).filter(
            NestedAttribute.attribute_id == attribute_id,
            NestedAttribute.is_active == True
        ).all()

    @staticmethod
    def get_nested_attribute_by_id(db: Session, nested_attribute_id: int) -> Optional[NestedAttribute]:
        return db.query(NestedAttribute).options(
            joinedload(NestedAttribute.nested_attribute).joinedload(Attribute.options),
            joinedload(NestedAttribute.nested_attribute).joinedload(Attribute.unit)
        ).filter(NestedAttribute.id == nested_attribute_id).first()

    @staticmethod
    def update_nested_attribute(db: Session, nested_attribute_id: int, data: NestedAttributeUpdate, updated_by: str = None) -> Optional[NestedAttribute]:
        nested_attribute = db.get(NestedAttribute, nested_attribute_id)
        if not nested_attribute:
            return None

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(nested_attribute, key, value)
        
        nested_attribute.updated_by = updated_by
        nested_attribute.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(nested_attribute)
        return nested_attribute

    @staticmethod
    def delete_nested_attribute(db: Session, nested_attribute_id: int) -> bool:
        nested_attribute = db.get(NestedAttribute, nested_attribute_id)
        if not nested_attribute:
            return False
        
        # Soft delete - just mark as inactive
        nested_attribute.is_active = False
        db.commit()
        return True

    # ============================================================================
    # UNIT METHODS
    # ============================================================================
    
    @staticmethod
    def create_unit(db: Session, data: UnitCreate, created_by: str = None) -> UnitResponse:
        unit = Unit(
            name=data.name,
            symbol=data.symbol,
            description=data.description,
            is_active=data.is_active,
            created_by=created_by
        )
        db.add(unit)
        db.commit()
        db.refresh(unit)
        return unit

    @staticmethod
    def get_unit_by_id(db: Session, unit_id: int) -> Optional[Unit]:
        return db.query(Unit).options(
            joinedload(Unit.attributes)
        ).filter(Unit.id == unit_id).first()

    @staticmethod
    def get_unit_by_name(db: Session, name: str) -> Optional[Unit]:
        return db.query(Unit).filter(Unit.name == name).first()

    @staticmethod
    def get_all_units(db: Session, skip: int = 0, limit: int = 100) -> List[Unit]:
        return db.query(Unit).options(
            joinedload(Unit.attributes)
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_active_units(db: Session) -> List[Unit]:
        return db.query(Unit).options(
            joinedload(Unit.attributes)
        ).filter(Unit.is_active == True).all()

    @staticmethod
    def update_unit(db: Session, unit_id: int, data: UnitUpdate, updated_by: str = None) -> Optional[Unit]:
        unit = db.get(Unit, unit_id)
        if not unit:
            return None

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(unit, key, value)
        
        unit.updated_by = updated_by
        unit.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(unit)
        return unit

    @staticmethod
    def delete_unit(db: Session, unit_id: int) -> bool:
        unit = db.get(Unit, unit_id)
        if not unit:
            return False
        
        # Soft delete - just mark as inactive
        unit.is_active = False
        db.commit()
        return True
