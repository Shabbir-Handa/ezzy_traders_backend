"""
Door and Attribute Management CRUD Operations
"""

from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from db_helper.models import DoorType, Attribute, EntityAttribute, AttributeOption, NestedAttribute, Unit, \
    DoorTypeThicknessOption
from schemas.schemas import (
    DoorTypeCreate, DoorTypeUpdate, DoorTypeResponse,
    AttributeCreate, AttributeUpdate, AttributeResponse,
    EntityAttributeCreate, EntityAttributeUpdate, EntityAttributeResponse,
    AttributeOptionCreate, AttributeOptionUpdate, AttributeOptionResponse,
    NestedAttributeCreate, NestedAttributeUpdate, NestedAttributeResponse,
    UnitCreate, UnitUpdate, UnitResponse,
    DoorTypeThicknessOptionCreate, DoorTypeThicknessOptionUpdate, DoorTypeThicknessOptionResponse
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
                    door_type_id=door_type.id,
                    created_by=username,
                    updated_by=username
                )
                db.add(db_thickness_option)
        db.commit()
        return door_type

    @staticmethod
    def get_door_type_by_id(db: Session, door_type_id: int) -> Optional[DoorTypeResponse]:
        return db.query(DoorType).options(
            joinedload(DoorType.attributes).joinedload(EntityAttribute.attribute),
            joinedload(DoorType.thickness_options)
        ).filter(DoorType.id == door_type_id).first()

    @staticmethod
    def get_all_door_types(db: Session, skip: int = 0, limit: int = 100) -> List[DoorTypeResponse]:
        return db.query(DoorType).options(
            joinedload(DoorType.entity_attributes).joinedload(EntityAttribute.attribute).joinedload(Attribute.options),
            joinedload(DoorType.thickness_options)
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_active_door_types(db: Session) -> List[DoorTypeResponse]:
        return db.query(DoorType).options(
            joinedload(DoorType.attributes).joinedload(EntityAttribute.attribute),
            joinedload(DoorType.thickness_options)
        ).filter(DoorType.is_active == True).all()

    @staticmethod
    def update_door_type(db: Session, door_type_id: int, data: DoorTypeUpdate, username: str = None) -> Optional[
        DoorTypeResponse]:
        door_type = db.get(DoorType, door_type_id)
        if not door_type:
            return None

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(door_type, key, value)

        door_type.updated_by = username
        door_type.updated_at = datetime.now(timezone.utc)

        db.commit()
        return door_type

    @staticmethod
    def disable_door_type(db: Session, door_type_id: int) -> bool:
        door_type = db.get(DoorType, door_type_id)
        if not door_type:
            return False

        door_type.is_active = False
        db.commit()
        return True

    @staticmethod
    def delete_door_type(db: Session, door_type_id: int) -> bool:
        door_type = db.get(DoorType, door_type_id)
        if not door_type:
            return False

        # Soft delete - just mark as inactive
        db.delete(door_type)
        db.commit()
        return True

    # ============================================================================
    # ATTRIBUTE METHODS
    # ============================================================================

    @staticmethod
    def create_attribute(db: Session, data: AttributeCreate, username: str = None) -> AttributeResponse:
        attribute = Attribute(
            **data.dict(exclude="options"),
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
        db.commit()
        return attribute

    @staticmethod
    def get_attribute_by_id(db: Session, attribute_id: int) -> Optional[AttributeResponse]:
        return db.query(Attribute).options(
            joinedload(Attribute.options).joinedload(AttributeOption.unit),
            joinedload(Attribute.unit)
        ).filter(Attribute.id == attribute_id).first()

    @staticmethod
    def get_all_attributes(db: Session, skip: int = 0, limit: int = 100) -> List[AttributeResponse]:
        return db.query(Attribute).options(
            joinedload(Attribute.options).joinedload(AttributeOption.unit),
            joinedload(Attribute.unit)
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_active_attributes(db: Session) -> List[AttributeResponse]:
        return db.query(Attribute).options(
            joinedload(Attribute.options).joinedload(AttributeOption.unit),
            joinedload(Attribute.unit)
        ).filter(Attribute.is_active == True).all()

    @staticmethod
    def update_attribute(db: Session, attribute_id: int, data: AttributeUpdate, username: str = None) -> Optional[
        AttributeResponse]:
        attribute = db.get(Attribute, attribute_id)
        if not attribute:
            return None

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(attribute, key, value)

        attribute.updated_by = username
        attribute.updated_at = datetime.now(timezone.utc)

        db.commit()
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
    def create_entity_attribute(db: Session, data: EntityAttributeCreate,
                                username: str = None) -> EntityAttributeResponse:
        entity_attribute = EntityAttribute(
            **data.dict(),
            created_by=username,
            updated_by=username
        )
        db.add(entity_attribute)
        db.commit()
        return entity_attribute

    @staticmethod
    def get_entity_attributes_by_entity(db: Session, entity_type: str, entity_id: int) -> List[EntityAttributeResponse]:
        return db.query(EntityAttribute).options(
            joinedload(EntityAttribute.attribute)
        ).filter(
            EntityAttribute.entity_type == entity_type,
            EntityAttribute.entity_id == entity_id
        ).order_by(EntityAttribute.order).all()

    @staticmethod
    def get_entity_attributes_by_entity_type(db: Session, entity_type: str, skip: int = 0, limit: int = 100) -> List[EntityAttributeResponse]:
        """Get all entity attributes for a specific entity type"""
        return db.query(EntityAttribute).options(
            joinedload(EntityAttribute.attribute)
        ).filter(
            EntityAttribute.entity_type == entity_type
        ).order_by(EntityAttribute.entity_id, EntityAttribute.order).offset(skip).limit(limit).all()

    @staticmethod
    def get_all_entity_attributes(db: Session, skip: int = 0, limit: int = 100) -> List[EntityAttributeResponse]:
        """Get all entity attributes with pagination"""
        return db.query(EntityAttribute).options(
            joinedload(EntityAttribute.attribute)
        ).order_by(EntityAttribute.entity_type, EntityAttribute.entity_id, EntityAttribute.order).offset(skip).limit(limit).all()

    @staticmethod
    def get_entity_attribute_by_id(db: Session, entity_attribute_id: int) -> Optional[EntityAttributeResponse]:
        return db.query(EntityAttribute).options(
            joinedload(EntityAttribute.attribute)
        ).filter(EntityAttribute.id == entity_attribute_id).first()

    @staticmethod
    def update_entity_attribute(db: Session, entity_attribute_id: int, data: EntityAttributeUpdate,
                                username: str = None) -> Optional[EntityAttributeResponse]:
        entity_attribute = db.get(EntityAttribute, entity_attribute_id)
        if not entity_attribute:
            return None

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(entity_attribute, key, value)

        entity_attribute.updated_by = username
        entity_attribute.updated_at = datetime.now(timezone.utc)

        db.commit()
        return entity_attribute

    @staticmethod
    def delete_entity_attribute(db: Session, entity_attribute_id: int) -> bool:
        entity_attribute = db.get(EntityAttribute, entity_attribute_id)
        if not entity_attribute:
            return False

        # Soft delete - just mark as inactive
        db.delete(entity_attribute)
        db.commit()
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
        db.commit()
        return attribute_option

    @staticmethod
    def get_attribute_options_by_attribute(db: Session, attribute_id: int) -> List[AttributeOptionResponse]:
        return db.query(AttributeOption).filter(
            AttributeOption.attribute_id == attribute_id,
            AttributeOption.is_active == True
        ).all()

    @staticmethod
    def get_attribute_option_by_id(db: Session, option_id: int) -> Optional[AttributeOptionResponse]:
        return db.query(AttributeOption).filter(AttributeOption.id == option_id).first()

    @staticmethod
    def update_attribute_option(db: Session, option_id: int, data: AttributeOptionUpdate, username: str = None) -> \
    Optional[AttributeOptionResponse]:
        attribute_option = db.get(AttributeOption, option_id)
        if not attribute_option:
            return None

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(attribute_option, key, value)

        attribute_option.updated_by = username
        attribute_option.updated_at = datetime.now(timezone.utc)

        db.commit()
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
    def create_nested_attribute(db: Session, data: NestedAttributeCreate,
                                username: str = None) -> NestedAttributeResponse:
        # Validate the relationship before creating
        validation = DoorAttributeCRUD.validate_nested_attribute_relationship(
            db, data.parent_attribute_id, data.child_attribute_id
        )

        if not validation['is_valid']:
            raise ValueError(f"Invalid nested attribute relationship: {'; '.join(validation['errors'])}")

        nested_attribute = NestedAttribute(
            **data.dict(),
            created_by=username,
            updated_by=username
        )
        db.add(nested_attribute)
        db.commit()
        return nested_attribute

    @staticmethod
    def get_nested_attributes_by_attribute(db: Session, attribute_id: int) -> List[NestedAttributeResponse]:
        return db.query(NestedAttribute).options(
            joinedload(NestedAttribute.child_attribute).joinedload(Attribute.options),
            joinedload(NestedAttribute.child_attribute).joinedload(Attribute.unit)
        ).filter(
            NestedAttribute.parent_attribute_id == attribute_id,
            NestedAttribute.is_active == True
        ).all()

    @staticmethod
    def get_child_attributes_for_parent(db: Session, parent_attribute_id: int) -> List[AttributeResponse]:
        """Get all child attributes for a given parent attribute"""
        nested_attrs = db.query(NestedAttribute).options(
            joinedload(NestedAttribute.child_attribute)
        ).filter(
            NestedAttribute.parent_attribute_id == parent_attribute_id,
            NestedAttribute.is_active == True
        ).order_by(NestedAttribute.relationship_order).all()

        return [nested_attr.child_attribute for nested_attr in nested_attrs]

    @staticmethod
    def get_parent_attributes_for_child(db: Session, child_attribute_id: int) -> List[AttributeResponse]:
        """Get all parent attributes that contain a specific child attribute"""
        nested_attrs = db.query(NestedAttribute).options(
            joinedload(NestedAttribute.parent_attribute)
        ).filter(
            NestedAttribute.child_attribute_id == child_attribute_id,
            NestedAttribute.is_active == True
        ).all()

        return [nested_attr.parent_attribute for nested_attr in nested_attrs]

    @staticmethod
    def check_attribute_dependencies(db: Session, attribute_id: int) -> dict:
        """Check if an attribute has dependencies that would prevent deletion"""

        dependencies = {
            'has_nested_children': False,
            'has_nested_parents': False,
            'is_used_by_entities': False,
            'can_be_deleted': True,
            'dependency_details': []
        }

        # Check if it's a parent attribute (has nested children)
        nested_children = db.query(NestedAttribute).filter(
            NestedAttribute.parent_attribute_id == attribute_id,
            NestedAttribute.is_active == True
        ).count()

        if nested_children > 0:
            dependencies['has_nested_children'] = True
            dependencies['can_be_deleted'] = False
            dependencies['dependency_details'].append(f"Has {nested_children} nested child attributes")

        # Check if it's a child attribute (has nested parents)
        nested_parents = db.query(NestedAttribute).filter(
            NestedAttribute.child_attribute_id == attribute_id,
            NestedAttribute.is_active == True
        ).count()

        if nested_parents > 0:
            dependencies['has_nested_parents'] = True
            dependencies['can_be_deleted'] = False
            dependencies['dependency_details'].append(f"Used by {nested_parents} parent attributes")

        # Check if it's used by any entities
        entity_usage = db.query(EntityAttribute).filter(
            EntityAttribute.attribute_id == attribute_id
        ).count()

        if entity_usage > 0:
            dependencies['is_used_by_entities'] = True
            dependencies['can_be_deleted'] = False
            dependencies['dependency_details'].append(f"Used by {entity_usage} entities")

        return dependencies

    @staticmethod
    def get_attribute_hierarchy_tree(db: Session, attribute_id: int, max_depth: int = 5) -> dict:
        """Get the complete attribute hierarchy tree for a given attribute"""

        def build_tree(attr_id: int, depth: int = 0) -> dict:
            if depth > max_depth:
                return None

            attr = db.query(Attribute).filter(Attribute.id == attr_id).first()
            if not attr:
                return None

            tree = {
                'id': attr.id,
                'name': attr.name,
                'description': attr.description,
                'cost_type': attr.cost_type,
                'fixed_cost': attr.fixed_cost,
                'cost_per_unit': attr.cost_per_unit,
                'depth': depth,
                'children': []
            }

            # If it's a nested attribute, get children
            if attr.cost_type == 'nested':
                nested_children = db.query(NestedAttribute).filter(
                    NestedAttribute.parent_attribute_id == attr_id,
                    NestedAttribute.is_active == True
                ).order_by(NestedAttribute.relationship_order).all()

                for nested_child in nested_children:
                    child_tree = build_tree(nested_child.child_attribute_id, depth + 1)
                    if child_tree:
                        tree['children'].append(child_tree)

            return tree

        return build_tree(attribute_id)

    @staticmethod
    def bulk_create_nested_attributes(db: Session, parent_attribute_id: int, child_attribute_ids: List[int],
                                      username: str = None) -> List[NestedAttributeResponse]:
        """Bulk create nested attributes for a parent attribute"""
        nested_attributes = []

        for order, child_id in enumerate(child_attribute_ids, 1):
            nested_attr = NestedAttribute(
                parent_attribute_id=parent_attribute_id,
                child_attribute_id=child_id,
                relationship_order=order,
                is_active=True,
                created_by=username,
                updated_by=username
            )
            nested_attributes.append(nested_attr)

        db.add_all(nested_attributes)
        db.commit()

        return nested_attributes

    @staticmethod
    def validate_nested_attribute_relationship(db: Session, parent_attribute_id: int, child_attribute_id: int) -> dict:
        """Validate that a nested attribute relationship is valid (no circular dependencies)"""

        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }

        # Check if parent and child are the same
        if parent_attribute_id == child_attribute_id:
            validation_result['is_valid'] = False
            validation_result['errors'].append("Parent and child attributes cannot be the same")
            return validation_result

        # Check if both attributes exist
        parent_attr = db.query(Attribute).filter(Attribute.id == parent_attribute_id).first()
        child_attr = db.query(Attribute).filter(Attribute.id == child_attribute_id).first()

        if not parent_attr:
            validation_result['is_valid'] = False
            validation_result['errors'].append("Parent attribute does not exist")
            return validation_result

        if not child_attr:
            validation_result['is_valid'] = False
            validation_result['errors'].append("Child attribute does not exist")
            return validation_result

        # Check if parent attribute is of type 'nested'
        if parent_attr.cost_type != 'nested':
            validation_result['warnings'].append("Parent attribute is not of type 'nested'")

        # Check for circular dependencies
        if DoorAttributeCRUD._would_create_circular_dependency(db, parent_attribute_id, child_attribute_id):
            validation_result['is_valid'] = False
            validation_result['errors'].append("This relationship would create a circular dependency")

        return validation_result

    @staticmethod
    def _would_create_circular_dependency(db: Session, parent_id: int, child_id: int, visited: set = None) -> bool:
        """Helper method to check for circular dependencies"""
        if visited is None:
            visited = set()

        if parent_id in visited:
            return True

        visited.add(parent_id)

        # Check if the child is already a parent of the parent (directly or indirectly)
        nested_parents = db.query(NestedAttribute).filter(
            NestedAttribute.child_attribute_id == parent_id,
            NestedAttribute.is_active == True
        ).all()

        for nested_parent in nested_parents:
            if nested_parent.parent_attribute_id == child_id:
                return True

            if DoorAttributeCRUD._would_create_circular_dependency(db, nested_parent.parent_attribute_id, child_id,
                                                                   visited.copy()):
                return True

        return False

    @staticmethod
    def get_nested_attribute_cost_breakdown(
            db: Session,
            attribute_id: int,
            quantity: float = 1.0,
            child_options: Optional[Dict[int, int]] = None
    ) -> dict:
        """
        Get a detailed cost breakdown for a nested attribute
        
        Args:
            db: Database session
            attribute_id: ID of the nested attribute
            quantity: Quantity multiplier
            child_options: Dictionary mapping child_attribute_id to selected_option_id
        """

        breakdown = {
            'attribute_id': attribute_id,
            'total_cost': 0.0,
            'cost_components': [],
            'quantity': quantity,
            'has_nested_components': False
        }

        # Get the main attribute
        main_attribute = db.query(Attribute).filter(Attribute.id == attribute_id).first()
        if not main_attribute:
            return breakdown

        breakdown['attribute_name'] = main_attribute.name
        breakdown['cost_type'] = main_attribute.cost_type

        if main_attribute.cost_type != 'nested':
            # If it's not nested, return the direct cost
            if main_attribute.cost_type == 'constant':
                breakdown['total_cost'] = main_attribute.fixed_cost or 0.0
                breakdown['cost_components'].append({
                    'name': main_attribute.name,
                    'cost_type': 'constant',
                    'cost': main_attribute.fixed_cost or 0.0,
                    'description': 'Direct fixed cost'
                })
            elif main_attribute.cost_type == 'variable':
                cost = (main_attribute.cost_per_unit or 0.0) * quantity
                breakdown['total_cost'] = cost
                breakdown['cost_components'].append({
                    'name': main_attribute.name,
                    'cost_type': 'variable',
                    'cost_per_unit': main_attribute.cost_per_unit or 0.0,
                    'quantity': quantity,
                    'total_cost': cost,
                    'description': f'Variable cost per unit × {quantity}'
                })
            return breakdown

        # It's a nested attribute, get all child components
        breakdown['has_nested_components'] = True

        child_attributes = DoorAttributeCRUD.get_child_attributes_for_parent(db, attribute_id)

        for child_attr in child_attributes:
            # Get selected option for this child attribute if provided
            selected_option = None
            if child_options and child_attr.id in child_options:
                selected_option = db.query(AttributeOption).filter(
                    AttributeOption.id == child_options[child_attr.id]
                ).first()

            if child_attr.cost_type == 'constant':
                # Use selected option cost if available, otherwise fallback to attribute fixed_cost
                if selected_option:
                    cost = selected_option.cost
                    option_name = selected_option.name
                else:
                    cost = child_attr.fixed_cost or 0.0
                    option_name = "Default"

                breakdown['total_cost'] += cost
                breakdown['cost_components'].append({
                    'name': child_attr.name,
                    'cost_type': 'constant',
                    'cost': cost,
                    'selected_option': option_name,
                    'description': f'Fixed cost component: {option_name}'
                })

            elif child_attr.cost_type == 'variable':
                # Use selected option cost_per_unit if available, otherwise fallback to attribute cost_per_unit
                option_cost_per_unit = None
                if selected_option and getattr(selected_option, 'cost_per_unit', None):
                    option_cost_per_unit = selected_option.cost_per_unit

                cost_per_unit = option_cost_per_unit if option_cost_per_unit is not None else (
                            child_attr.cost_per_unit or 0.0)
                cost = cost_per_unit * quantity

                breakdown['total_cost'] += cost
                breakdown['cost_components'].append({
                    'name': child_attr.name,
                    'cost_type': 'variable',
                    'cost_per_unit': cost_per_unit,
                    'quantity': quantity,
                    'total_cost': cost,
                    'selected_option': selected_option.name if selected_option else None,
                    'description': f'Variable cost component × {quantity}'
                })

            elif child_attr.cost_type == 'nested':
                # Recursively get breakdown for nested child
                # Pass down child options for deeper nesting levels
                child_breakdown = DoorAttributeCRUD.get_nested_attribute_cost_breakdown(
                    db, child_attr.id, quantity, child_options
                )
                breakdown['total_cost'] += child_breakdown['total_cost']
                breakdown['cost_components'].append({
                    'name': child_attr.name,
                    'cost_type': 'nested',
                    'total_cost': child_breakdown['total_cost'],
                    'description': 'Nested component cost',
                    'sub_breakdown': child_breakdown
                })

        return breakdown

    @staticmethod
    def get_nested_attribute_by_id(db: Session, nested_attribute_id: int) -> Optional[NestedAttributeResponse]:
        return db.query(NestedAttribute).options(
            joinedload(NestedAttribute.child_attribute).joinedload(Attribute.options),
            joinedload(NestedAttribute.child_attribute).joinedload(Attribute.unit)
        ).filter(NestedAttribute.id == nested_attribute_id).first()

    @staticmethod
    def update_nested_attribute(db: Session, nested_attribute_id: int, data: NestedAttributeUpdate,
                                username: str = None) -> Optional[NestedAttributeResponse]:
        nested_attribute = db.get(NestedAttribute, nested_attribute_id)
        if not nested_attribute:
            return None

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(nested_attribute, key, value)

        nested_attribute.updated_by = username
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
    def create_unit(db: Session, data: UnitCreate, username: str = None) -> UnitResponse:
        unit = Unit(
            **data.dict(),
            created_by=username,
            updated_by=username
        )
        db.add(unit)
        db.commit()
        return unit

    @staticmethod
    def get_unit_by_id(db: Session, unit_id: int) -> Optional[UnitResponse]:
        return db.query(Unit).filter(Unit.id == unit_id).first()

    @staticmethod
    def get_all_units(db: Session, skip: int = 0, limit: int = 100) -> List[UnitResponse]:
        return db.query(Unit).offset(skip).limit(limit).all()

    @staticmethod
    def get_active_units(db: Session) -> List[UnitResponse]:
        return db.query(Unit).filter(Unit.is_active == True).all()

    @staticmethod
    def update_unit(db: Session, unit_id: int, data: UnitUpdate, username: str = None) -> Optional[UnitResponse]:
        unit = db.get(Unit, unit_id)
        if not unit:
            return None

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(unit, key, value)

        unit.updated_by = username
        unit.updated_at = datetime.now(timezone.utc)

        db.commit()
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

    # ============================================================================
    # DOOR TYPE THICKNESS OPTION METHODS
    # ============================================================================

    @staticmethod
    def create_door_type_thickness_option(db: Session, data: DoorTypeThicknessOptionCreate, username: str = None) -> DoorTypeThicknessOptionResponse:
        """Create a new door type thickness option"""
        thickness_option = DoorTypeThicknessOption(
            **data.dict(),
            created_by=username,
            updated_by=username
        )
        db.add(thickness_option)
        db.commit()
        db.refresh(thickness_option)
        return thickness_option

    @staticmethod
    def get_door_type_thickness_option_by_id(db: Session, thickness_option_id: int) -> Optional[DoorTypeThicknessOptionResponse]:
        """Get a door type thickness option by ID"""
        return db.query(DoorTypeThicknessOption).filter(DoorTypeThicknessOption.id == thickness_option_id).first()

    @staticmethod
    def get_door_type_thickness_options_by_door_type(db: Session, door_type_id: int) -> List[DoorTypeThicknessOptionResponse]:
        """Get all thickness options for a specific door type"""
        return db.query(DoorTypeThicknessOption).filter(
            DoorTypeThicknessOption.door_type_id == door_type_id,
            DoorTypeThicknessOption.is_active == True
        ).order_by(DoorTypeThicknessOption.thickness_value).all()

    @staticmethod
    def get_all_door_type_thickness_options(db: Session, skip: int = 0, limit: int = 100) -> List[DoorTypeThicknessOptionResponse]:
        """Get all door type thickness options with pagination"""
        return db.query(DoorTypeThicknessOption).options(
            joinedload(DoorTypeThicknessOption.door_type)
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_active_door_type_thickness_options(db: Session) -> List[DoorTypeThicknessOptionResponse]:
        """Get all active door type thickness options"""
        return db.query(DoorTypeThicknessOption).options(
            joinedload(DoorTypeThicknessOption.door_type)
        ).filter(DoorTypeThicknessOption.is_active == True).all()

    @staticmethod
    def update_door_type_thickness_option(db: Session, thickness_option_id: int, data: DoorTypeThicknessOptionUpdate, username: str = None) -> Optional[DoorTypeThicknessOptionResponse]:
        """Update a door type thickness option"""
        thickness_option = db.get(DoorTypeThicknessOption, thickness_option_id)
        if not thickness_option:
            return None

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(thickness_option, key, value)

        thickness_option.updated_by = username
        thickness_option.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(thickness_option)
        return thickness_option

    @staticmethod
    def delete_door_type_thickness_option(db: Session, thickness_option_id: int) -> bool:
        """Delete a door type thickness option (soft delete)"""
        thickness_option = db.get(DoorTypeThicknessOption, thickness_option_id)
        if not thickness_option:
            return False

        # Soft delete - just mark as inactive
        thickness_option.is_active = False
        thickness_option.updated_at = datetime.now(timezone.utc)
        db.commit()
        return True

    @staticmethod
    def get_door_type_by_name(db: Session, name: str) -> Optional[DoorTypeResponse]:
        """Get a door type by name"""
        return db.query(DoorType).filter(DoorType.name == name).first()

    @staticmethod
    def get_attribute_by_name(db: Session, name: str) -> Optional[AttributeResponse]:
        """Get an attribute by name"""
        return db.query(Attribute).filter(Attribute.name == name).first()

    @staticmethod
    def get_unit_by_name(db: Session, name: str) -> Optional[UnitResponse]:
        """Get a unit by name"""
        return db.query(Unit).filter(Unit.name == name).first()

    @staticmethod
    def get_attributes_by_domain(db: Session, domain: str) -> List[AttributeResponse]:
        """Get attributes by domain (placeholder for future domain-based filtering)"""
        return db.query(Attribute).options(
            joinedload(Attribute.options).joinedload(AttributeOption.unit),
            joinedload(Attribute.unit)
        ).filter(Attribute.is_active == True).all()
