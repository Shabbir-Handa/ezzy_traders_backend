"""
Door Type, Attribute, Nested Attribute, and Unit Management Endpoints
Routes contain NO business logic — all logic delegated to services.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.services.door_attribute_service import DoorAttributeService
from app.schemas.door_type import (
    DoorTypeCreate, DoorTypeUpdate, DoorTypeResponse, PaginatedDoorTypeResponse,
    DoorTypeThicknessOptionCreate, DoorTypeThicknessOptionUpdate, DoorTypeThicknessOptionResponse,
    DoorTypeAttributeCreate, DoorTypeAttributeUpdate, DoorTypeAttributeResponse,
)
from app.schemas.attribute import (
    AttributeCreate, AttributeUpdate, AttributeResponse, PaginatedAttributeResponse,
    AttributeOptionCreate, AttributeOptionUpdate, AttributeOptionResponse,
    NestedAttributeCreate, NestedAttributeUpdate, NestedAttributeResponse, PaginatedNestedAttributeResponse,
    NestedAttributeChildCreate, NestedAttributeChildUpdate, NestedAttributeChildResponse,
)
from app.schemas.unit import (
    UnitCreate, UnitUpdate, UnitResponse, PaginatedUnitResponse,
)
from app.core.security import get_current_user
from app.db.session import get_db

router = APIRouter(tags=["Door-Attribute-Management"])


# ============================================================================
# DOOR TYPE ENDPOINTS
# ============================================================================

@router.post("/door-types/", response_model=DoorTypeResponse, status_code=status.HTTP_201_CREATED)
def create_door_type(
        door_type_data: DoorTypeCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Create a new door type"""
    try:
        door_type = DoorAttributeService.create_door_type(db, door_type_data, current_user.username)
        db.commit()
        door_type = DoorAttributeService.get_door_type_by_id(db, door_type.id)
        return door_type
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.get("/door-types/", response_model=PaginatedDoorTypeResponse)
def get_door_types(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get all door types with pagination"""
    try:
        door_types = DoorAttributeService.get_all_door_types(db, skip=skip, limit=limit)
        total = DoorAttributeService.count_door_types(db)

        return {
            "data": door_types,
            "total": total,
            "page": (skip // limit) + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.get("/door-types/{door_type_id}", response_model=DoorTypeResponse)
def get_door_type(
        door_type_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get a specific door type by ID"""
    try:
        door_type = DoorAttributeService.get_door_type_by_id(db, door_type_id)
        if not door_type:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Door type not found")
        return door_type
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.put("/door-types/{door_type_id}", response_model=DoorTypeResponse)
def update_door_type(
        door_type_id: int,
        door_type_data: DoorTypeUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Update a door type"""
    try:
        door_type = DoorAttributeService.update_door_type(db, door_type_id, door_type_data, current_user.username)
        if not door_type:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Door type not found")
        db.commit()
        door_type = DoorAttributeService.get_door_type_by_id(db, door_type.id)
        return door_type
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.delete("/door-types/{door_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_door_type(
        door_type_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Delete a door type"""
    try:
        success = DoorAttributeService.delete_door_type(db, door_type_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Door type not found")
        db.commit()
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


# ============================================================================
# DOOR TYPE THICKNESS OPTION ENDPOINTS
# ============================================================================

@router.post("/door-type-thickness-options/", response_model=DoorTypeThicknessOptionResponse, status_code=status.HTTP_201_CREATED)
def create_door_type_thickness_option(
        thickness_option_data: DoorTypeThicknessOptionCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Create a new door type thickness option"""
    try:
        option = DoorAttributeService.create_door_type_thickness_option(db, thickness_option_data, current_user.username)
        db.commit()
        return option
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.get("/door-types/{door_type_id}/thickness-options", response_model=List[DoorTypeThicknessOptionResponse])
def get_door_type_thickness_options(
        door_type_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get all thickness options for a door type"""
    try:
        options = DoorAttributeService.get_door_type_thickness_options_by_door_type(db, door_type_id)
        return options
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.put("/door-type-thickness-options/{thickness_option_id}", response_model=DoorTypeThicknessOptionResponse)
def update_door_type_thickness_option(
        thickness_option_id: int,
        thickness_option_data: DoorTypeThicknessOptionUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Update a door type thickness option"""
    try:
        option = DoorAttributeService.update_door_type_thickness_option(db, thickness_option_id, thickness_option_data, current_user.username)
        if not option:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thickness option not found")
        db.commit()
        return option
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.delete("/door-type-thickness-options/{thickness_option_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_door_type_thickness_option(
        thickness_option_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Delete a door type thickness option"""
    try:
        success = DoorAttributeService.delete_door_type_thickness_option(db, thickness_option_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thickness option not found")
        db.commit()
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


# ============================================================================
# ATTRIBUTE ENDPOINTS
# ============================================================================

@router.post("/attributes/", response_model=AttributeResponse, status_code=status.HTTP_201_CREATED)
def create_attribute(
        attribute_data: AttributeCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Create a new attribute"""
    try:
        attribute = DoorAttributeService.create_attribute(db, attribute_data, current_user.username)
        db.commit()
        attribute = DoorAttributeService.get_attribute_by_id(db, attribute.id)
        return attribute
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.get("/attributes/", response_model=PaginatedAttributeResponse)
def get_attributes(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get all attributes with pagination"""
    try:
        attributes = DoorAttributeService.get_all_attributes(db, skip=skip, limit=limit)
        total = DoorAttributeService.count_attributes(db)

        return {
            "data": attributes,
            "total": total,
            "page": (skip // limit) + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.get("/attributes/{attribute_id}", response_model=AttributeResponse)
def get_attribute(
        attribute_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get a specific attribute by ID"""
    try:
        attribute = DoorAttributeService.get_attribute_by_id(db, attribute_id)
        if not attribute:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute not found")
        return attribute
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.put("/attributes/{attribute_id}", response_model=AttributeResponse)
def update_attribute(
        attribute_id: int,
        attribute_data: AttributeUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Update an attribute"""
    try:
        attribute = DoorAttributeService.update_attribute(db, attribute_id, attribute_data, current_user.username)
        if not attribute:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute not found")
        db.commit()
        attribute = DoorAttributeService.get_attribute_by_id(db, attribute.id)
        return attribute
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.delete("/attributes/{attribute_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attribute(
        attribute_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Delete an attribute"""
    try:
        success = DoorAttributeService.delete_attribute(db, attribute_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute not found")
        db.commit()
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


# ============================================================================
# DOOR TYPE ATTRIBUTE ENDPOINTS
# ============================================================================

@router.post("/door-type-attributes/", response_model=DoorTypeAttributeResponse, status_code=status.HTTP_201_CREATED)
def create_door_type_attribute(
        door_type_attribute_data: DoorTypeAttributeCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Create a new door type attribute association"""
    try:
        dta = DoorAttributeService.create_door_type_attribute(db, door_type_attribute_data, current_user.username)
        db.commit()
        dta = DoorAttributeService.get_door_type_attribute_by_id(db, dta.id)
        return dta
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.get("/door-types/{door_type_id}/attributes", response_model=List[DoorTypeAttributeResponse])
def get_door_type_attributes(
        door_type_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get all attributes for a door type"""
    try:
        attributes = DoorAttributeService.get_door_type_attributes_by_door_type(db, door_type_id)
        return attributes
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.put("/door-type-attributes/{door_type_attribute_id}", response_model=DoorTypeAttributeResponse)
def update_door_type_attribute(
        door_type_attribute_id: int,
        door_type_attribute_data: DoorTypeAttributeUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Update a door type attribute association"""
    try:
        dta = DoorAttributeService.update_door_type_attribute(db, door_type_attribute_id, door_type_attribute_data, current_user.username)
        if not dta:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Door type attribute not found")
        db.commit()
        dta = DoorAttributeService.get_door_type_attribute_by_id(db, dta.id)
        return dta
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.delete("/door-type-attributes/{door_type_attribute_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_door_type_attribute(
        door_type_attribute_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Delete a door type attribute association"""
    try:
        success = DoorAttributeService.delete_door_type_attribute(db, door_type_attribute_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Door type attribute not found")
        db.commit()
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


# ============================================================================
# ATTRIBUTE OPTION ENDPOINTS
# ============================================================================

@router.post("/attribute-options/", response_model=AttributeOptionResponse, status_code=status.HTTP_201_CREATED)
def create_attribute_option(
        attribute_option_data: AttributeOptionCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Create a new attribute option"""
    try:
        option = DoorAttributeService.create_attribute_option(db, attribute_option_data, current_user.username)
        db.commit()
        return option
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.get("/attributes/{attribute_id}/options", response_model=List[AttributeOptionResponse])
def get_attribute_options(
        attribute_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get all options for an attribute"""
    try:
        options = DoorAttributeService.get_attribute_options_by_attribute(db, attribute_id)
        return options
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.put("/attribute-options/{option_id}", response_model=AttributeOptionResponse)
def update_attribute_option(
        option_id: int,
        attribute_option_data: AttributeOptionUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Update an attribute option"""
    try:
        option = DoorAttributeService.update_attribute_option(db, option_id, attribute_option_data, current_user.username)
        if not option:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute option not found")
        db.commit()
        return option
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.delete("/attribute-options/{option_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attribute_option(
        option_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Delete an attribute option"""
    try:
        success = DoorAttributeService.delete_attribute_option(db, option_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute option not found")
        db.commit()
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


# ============================================================================
# NESTED ATTRIBUTE ENDPOINTS
# ============================================================================

@router.post("/nested-attributes/", response_model=NestedAttributeResponse, status_code=status.HTTP_201_CREATED)
def create_nested_attribute(
        nested_attribute_data: NestedAttributeCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Create a new nested attribute"""
    try:
        nested = DoorAttributeService.create_nested_attribute(db, nested_attribute_data, current_user.username)
        db.commit()
        nested = DoorAttributeService.get_nested_attribute_by_id(db, nested.id)
        return nested
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.get("/nested-attributes/", response_model=PaginatedNestedAttributeResponse)
def get_nested_attributes(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get all nested attributes with pagination"""
    try:
        nested_attributes = DoorAttributeService.get_all_nested_attributes(db, skip=skip, limit=limit)
        total = DoorAttributeService.count_nested_attributes(db)

        return {
            "data": nested_attributes,
            "total": total,
            "page": (skip // limit) + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.get("/nested-attributes/{nested_attribute_id}", response_model=NestedAttributeResponse)
def get_nested_attribute(
        nested_attribute_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get a specific nested attribute by ID"""
    try:
        nested = DoorAttributeService.get_nested_attribute_by_id(db, nested_attribute_id)
        if not nested:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nested attribute not found")
        return nested
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.put("/nested-attributes/{nested_attribute_id}", response_model=NestedAttributeResponse)
def update_nested_attribute(
        nested_attribute_id: int,
        nested_attribute_data: NestedAttributeUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Update a nested attribute"""
    try:
        nested = DoorAttributeService.update_nested_attribute(db, nested_attribute_id, nested_attribute_data, current_user.username)
        if not nested:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nested attribute not found")
        db.commit()
        nested = DoorAttributeService.get_nested_attribute_by_id(db, nested.id)
        return nested
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.delete("/nested-attributes/{nested_attribute_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_nested_attribute(
        nested_attribute_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Delete a nested attribute"""
    try:
        success = DoorAttributeService.delete_nested_attribute(db, nested_attribute_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nested attribute not found")
        db.commit()
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


# ============================================================================
# NESTED ATTRIBUTE CHILD ENDPOINTS
# ============================================================================

@router.post("/nested-attribute-children/", response_model=NestedAttributeChildResponse, status_code=status.HTTP_201_CREATED)
def create_nested_attribute_child(
        nested_attribute_child_data: NestedAttributeChildCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Create a new nested attribute child"""
    try:
        child = DoorAttributeService.create_nested_attribute_child(db, nested_attribute_child_data, current_user.username)
        db.commit()
        child = DoorAttributeService.get_nested_attribute_child_by_id(db, child.id)
        return child
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.get("/nested-attributes/{nested_attribute_id}/children", response_model=List[NestedAttributeChildResponse])
def get_nested_attribute_children(
        nested_attribute_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get all children for a nested attribute"""
    try:
        children = DoorAttributeService.get_nested_attribute_children_by_nested_attribute(db, nested_attribute_id)
        return children
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.put("/nested-attribute-children/{nested_attribute_child_id}", response_model=NestedAttributeChildResponse)
def update_nested_attribute_child(
        nested_attribute_child_id: int,
        nested_attribute_child_data: NestedAttributeChildUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Update a nested attribute child"""
    try:
        child = DoorAttributeService.update_nested_attribute_child(db, nested_attribute_child_id, nested_attribute_child_data, current_user.username)
        if not child:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nested attribute child not found")
        db.commit()
        child = DoorAttributeService.get_nested_attribute_child_by_id(db, child.id)
        return child
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.delete("/nested-attribute-children/{nested_attribute_child_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_nested_attribute_child(
        nested_attribute_child_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Delete a nested attribute child"""
    try:
        success = DoorAttributeService.delete_nested_attribute_child(db, nested_attribute_child_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nested attribute child not found")
        db.commit()
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


# ============================================================================
# UNIT ENDPOINTS
# ============================================================================

@router.post("/units/", response_model=UnitResponse, status_code=status.HTTP_201_CREATED)
def create_unit(
        unit_data: UnitCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Create a new unit"""
    try:
        unit = DoorAttributeService.create_unit(db, unit_data, current_user.username)
        db.commit()
        return unit
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.get("/units/", response_model=PaginatedUnitResponse)
def get_units(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get all units with pagination"""
    try:
        units = DoorAttributeService.get_all_units(db, skip=skip, limit=limit)
        total = DoorAttributeService.count_units(db)

        return {
            "data": units,
            "total": total,
            "page": (skip // limit) + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.get("/units/{unit_id}", response_model=UnitResponse)
def get_unit(
        unit_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get a specific unit by ID"""
    try:
        unit = DoorAttributeService.get_unit_by_id(db, unit_id)
        if not unit:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found")
        return unit
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.put("/units/{unit_id}", response_model=UnitResponse)
def update_unit(
        unit_id: int,
        unit_data: UnitUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Update a unit"""
    try:
        unit = DoorAttributeService.update_unit(db, unit_id, unit_data, current_user.username)
        if not unit:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found")
        db.commit()
        return unit
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")


@router.delete("/units/{unit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_unit(
        unit_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Delete a unit"""
    try:
        success = DoorAttributeService.delete_unit(db, unit_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found")
        db.commit()
    except HTTPException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database service unavailable: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")
