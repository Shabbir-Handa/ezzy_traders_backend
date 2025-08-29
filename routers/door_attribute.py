"""
Door and Attribute Management Router
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from dependencies import get_db, get_current_user
from db_helper.door_attribute_crud import DoorAttributeCRUD
from schemas.schemas import (
    DoorTypeCreate, DoorTypeUpdate, DoorTypeResponse,
    AttributeCreate, AttributeUpdate, AttributeResponse,
    EntityAttributeCreate, EntityAttributeUpdate, EntityAttributeResponse,
    AttributeOptionCreate, AttributeOptionUpdate, AttributeOptionResponse,
    NestedAttributeCreate, NestedAttributeUpdate, NestedAttributeResponse,
    UnitCreate, UnitUpdate, UnitResponse
)

router = APIRouter(
    prefix="/api/door-attribute",
    tags=["Door & Attribute Management"],
)


# ============================================================================
# DOOR TYPE ENDPOINTS
# ============================================================================

@router.post("/door-types", response_model=DoorTypeResponse, status_code=status.HTTP_201_CREATED)
def create_door_type(
        door_type_data: DoorTypeCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Create a new door type"""
    try:
        # Check if door type name already exists
        existing_door_type = DoorAttributeCRUD.get_door_type_by_name(db, door_type_data.name)
        if existing_door_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Door type with this name already exists"
            )

        door_type = DoorAttributeCRUD.create_door_type(db, door_type_data, current_user.username)
        return door_type
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


@router.get("/door-types", response_model=List[DoorTypeResponse])
def get_door_types(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        active_only: bool = Query(False),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get all door types with pagination"""
    try:
        if active_only:
            door_types = DoorAttributeCRUD.get_active_door_types(db)
        else:
            door_types = DoorAttributeCRUD.get_all_door_types(db, skip=skip, limit=limit)
        return door_types
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


@router.get("/door-types/{door_type_id}", response_model=DoorTypeResponse)
def get_door_type(
        door_type_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get a specific door type by ID"""
    try:
        door_type = DoorAttributeCRUD.get_door_type_by_id(db, door_type_id)
        if not door_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Door type not found"
            )
        return door_type
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


@router.put("/door-types/{door_type_id}", response_model=DoorTypeResponse)
def update_door_type(
        door_type_id: int,
        door_type_data: DoorTypeUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Update a door type"""
    try:
        door_type = DoorAttributeCRUD.update_door_type(db, door_type_id, door_type_data, current_user.username)
        if not door_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Door type not found"
            )
        return door_type
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


@router.delete("/door-types/{door_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_door_type(
        door_type_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Delete a door type (soft delete)"""
    try:
        success = DoorAttributeCRUD.delete_door_type(db, door_type_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Door type not found"
            )
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


# ============================================================================
# ATTRIBUTE ENDPOINTS
# ============================================================================

@router.post("/attributes", response_model=AttributeResponse, status_code=status.HTTP_201_CREATED)
def create_attribute(
        attribute_data: AttributeCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Create a new attribute"""
    try:
        # Check if attribute name already exists
        existing_attribute = DoorAttributeCRUD.get_attribute_by_name(db, attribute_data.name)
        if existing_attribute:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attribute with this name already exists"
            )

        attribute = DoorAttributeCRUD.create_attribute(db, attribute_data, current_user.username)
        return attribute
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


@router.get("/attributes", response_model=List[AttributeResponse])
def get_attributes(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        domain: Optional[str] = Query(None),
        active_only: bool = Query(False),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get all attributes with pagination and optional domain filtering"""
    try:
        if domain:
            attributes = DoorAttributeCRUD.get_attributes_by_domain(db, domain)
        elif active_only:
            attributes = DoorAttributeCRUD.get_active_attributes(db)
        else:
            attributes = DoorAttributeCRUD.get_all_attributes(db, skip=skip, limit=limit)
        return attributes
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


@router.get("/attributes/{attribute_id}", response_model=AttributeResponse)
def get_attribute(
        attribute_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get a specific attribute by ID"""
    try:
        attribute = DoorAttributeCRUD.get_attribute_by_id(db, attribute_id)
        if not attribute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attribute not found"
            )
        return attribute
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


@router.put("/attributes/{attribute_id}", response_model=AttributeResponse)
def update_attribute(
        attribute_id: int,
        attribute_data: AttributeUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Update an attribute"""
    try:
        attribute = DoorAttributeCRUD.update_attribute(db, attribute_id, attribute_data, current_user.username)
        if not attribute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attribute not found"
            )
        return attribute
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


@router.delete("/attributes/{attribute_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attribute(
        attribute_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Delete an attribute (soft delete)"""
    try:
        success = DoorAttributeCRUD.delete_attribute(db, attribute_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attribute not found"
            )
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


# ============================================================================
# ENTITY ATTRIBUTE ENDPOINTS
# ============================================================================

@router.post("/entity-attributes", response_model=EntityAttributeResponse, status_code=status.HTTP_201_CREATED)
def create_entity_attribute(
        entity_attribute_data: EntityAttributeCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Create a new entity attribute relationship"""
    try:
        entity_attribute = DoorAttributeCRUD.create_entity_attribute(db, entity_attribute_data, current_user.username)
        return entity_attribute
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


@router.get("/entity-attributes", response_model=List[EntityAttributeResponse])
def get_entity_attributes(
        entity_type: str = Query(...),
        entity_id: int = Query(...),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get all attributes for a specific entity"""
    try:
        entity_attributes = DoorAttributeCRUD.get_entity_attributes_by_entity(db, entity_type, entity_id)
        return entity_attributes
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


@router.get("/entity-attributes/{entity_attribute_id}", response_model=EntityAttributeResponse)
def get_entity_attribute(
        entity_attribute_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get a specific entity attribute by ID"""
    try:
        entity_attribute = DoorAttributeCRUD.get_entity_attribute_by_id(db, entity_attribute_id)
        if not entity_attribute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entity attribute not found"
            )
        return entity_attribute
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


@router.put("/entity-attributes/{entity_attribute_id}", response_model=EntityAttributeResponse)
def update_entity_attribute(
        entity_attribute_id: int,
        entity_attribute_data: EntityAttributeUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Update an entity attribute"""
    try:
        entity_attribute = DoorAttributeCRUD.update_entity_attribute(db, entity_attribute_id, entity_attribute_data,
                                                                     current_user.username)
        if not entity_attribute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entity attribute not found"
            )
        return entity_attribute
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


@router.delete("/entity-attributes/{entity_attribute_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entity_attribute(
        entity_attribute_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Delete an entity attribute (soft delete)"""
    try:
        success = DoorAttributeCRUD.delete_entity_attribute(db, entity_attribute_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entity attribute not found"
            )
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


# ============================================================================
# ATTRIBUTE OPTION ENDPOINTS
# ============================================================================

@router.post("/attribute-options", response_model=AttributeOptionResponse, status_code=status.HTTP_201_CREATED)
def create_attribute_option(
        attribute_option_data: AttributeOptionCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Create a new attribute option"""
    try:
        attribute_option = DoorAttributeCRUD.create_attribute_option(db, attribute_option_data, current_user.username)
        return attribute_option
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


@router.get("/attribute-options", response_model=List[AttributeOptionResponse])
def get_attribute_options(
        attribute_id: int = Query(...),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get all options for a specific attribute"""
    try:
        attribute_options = DoorAttributeCRUD.get_attribute_options_by_attribute(db, attribute_id)
        return attribute_options
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


@router.get("/attribute-options/{option_id}", response_model=AttributeOptionResponse)
def get_attribute_option(
        option_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get a specific attribute option by ID"""
    try:
        attribute_option = DoorAttributeCRUD.get_attribute_option_by_id(db, option_id)
        if not attribute_option:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attribute option not found"
            )
        return attribute_option
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


@router.put("/attribute-options/{option_id}", response_model=AttributeOptionResponse)
def update_attribute_option(
        option_id: int,
        attribute_option_data: AttributeOptionUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Update an attribute option"""
    try:
        attribute_option = DoorAttributeCRUD.update_attribute_option(db, option_id, attribute_option_data,
                                                                     current_user.username)
        if not attribute_option:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attribute option not found"
            )
        return attribute_option
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


@router.delete("/attribute-options/{option_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attribute_option(
        option_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Delete an attribute option (soft delete)"""
    try:
        success = DoorAttributeCRUD.delete_attribute_option(db, option_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attribute option not found"
            )
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


# ============================================================================
# NESTED ATTRIBUTE ENDPOINTS
# ============================================================================

@router.post("/nested-attributes", response_model=NestedAttributeResponse, status_code=status.HTTP_201_CREATED)
def create_nested_attribute(
        nested_attribute_data: NestedAttributeCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Create a new nested attribute"""
    try:
        nested_attribute = DoorAttributeCRUD.create_nested_attribute(db, nested_attribute_data, current_user.username)
        return nested_attribute
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


@router.get("/nested-attributes", response_model=List[NestedAttributeResponse])
def get_nested_attributes(
        attribute_id: int = Query(...),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get all nested attributes for a specific attribute"""
    try:
        nested_attributes = DoorAttributeCRUD.get_nested_attributes_by_attribute(db, attribute_id)
        return nested_attributes
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


@router.get("/nested-attributes/{nested_attribute_id}", response_model=NestedAttributeResponse)
def get_nested_attribute(
        nested_attribute_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get a specific nested attribute by ID"""
    try:
        nested_attribute = DoorAttributeCRUD.get_nested_attribute_by_id(db, nested_attribute_id)
        if not nested_attribute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nested attribute not found"
            )
        return nested_attribute
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


@router.put("/nested-attributes/{nested_attribute_id}", response_model=NestedAttributeResponse)
def update_nested_attribute(
        nested_attribute_id: int,
        nested_attribute_data: NestedAttributeUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Update a nested attribute"""
    try:
        nested_attribute = DoorAttributeCRUD.update_nested_attribute(db, nested_attribute_id, nested_attribute_data,
                                                                     current_user.username)
        if not nested_attribute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nested attribute not found"
            )
        return nested_attribute
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


@router.delete("/nested-attributes/{nested_attribute_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_nested_attribute(
        nested_attribute_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Delete a nested attribute (soft delete)"""
    try:
        success = DoorAttributeCRUD.delete_nested_attribute(db, nested_attribute_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nested attribute not found"
            )
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


# ============================================================================
# UNIT ENDPOINTS
# ============================================================================

@router.post("/units", response_model=UnitResponse, status_code=status.HTTP_201_CREATED)
def create_unit(
        unit_data: UnitCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Create a new unit"""
    try:
        # Check if unit name already exists
        existing_unit = DoorAttributeCRUD.get_unit_by_name(db, unit_data.name)
        if existing_unit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unit with this name already exists"
            )

        unit = DoorAttributeCRUD.create_unit(db, unit_data, current_user.username)
        return unit
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


@router.get("/units", response_model=List[UnitResponse])
def get_units(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        active_only: bool = Query(False),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get all units with pagination"""
    try:
        if active_only:
            units = DoorAttributeCRUD.get_active_units(db)
        else:
            units = DoorAttributeCRUD.get_all_units(db, skip=skip, limit=limit)
        return units
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


@router.get("/units/{unit_id}", response_model=UnitResponse)
def get_unit(
        unit_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get a specific unit by ID"""
    try:
        unit = DoorAttributeCRUD.get_unit_by_id(db, unit_id)
        if not unit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unit not found"
            )
        return unit
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


@router.put("/units/{unit_id}", response_model=UnitResponse)
def update_unit(
        unit_id: int,
        unit_data: UnitUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Update a unit"""
    try:
        unit = DoorAttributeCRUD.update_unit(db, unit_id, unit_data, current_user.username)
        if not unit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unit not found"
            )
        return unit
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


@router.delete("/units/{unit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_unit(
        unit_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Delete a unit (soft delete)"""
    try:
        success = DoorAttributeCRUD.delete_unit(db, unit_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unit not found"
            )
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )
