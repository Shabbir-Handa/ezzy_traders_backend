"""
Employee and Role Management Router
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from db_helper.employee_role_crud import EmployeeRoleCRUD
from schemas.schemas import (
    RoleCreate, RoleUpdate, RoleResponse,
    PagePermissionCreate, PagePermissionUpdate, PagePermissionResponse,
    RolePermissionCreate, RolePermissionUpdate, RolePermissionResponse,
    EmployeeCreate, EmployeeUpdate, EmployeeResponse
)

from dependencies import get_db, get_current_user

router = APIRouter(
    prefix="/api/employee-role",
    tags=["Employee-Role-Management"],
)


# ============================================================================
# ROLE ENDPOINTS
# ============================================================================

@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new role"""
    try:
        # Check if role name already exists
        existing_role = EmployeeRoleCRUD.get_role_by_name(db, role_data.name)
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role with this name already exists"
            )
        
        role = EmployeeRoleCRUD.create_role(db, role_data, created_by=current_user.username)
        return role
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


@router.get("/roles", response_model=List[RoleResponse])
def get_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all roles with pagination"""
    try:
        if active_only:
            roles = EmployeeRoleCRUD.get_active_roles(db)
        else:
            roles = EmployeeRoleCRUD.get_all_roles(db, skip=skip, limit=limit)
        return roles
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


@router.get("/roles/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific role by ID"""
    try:
        role = EmployeeRoleCRUD.get_role_by_id(db, role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        return role
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


@router.put("/roles/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a role"""
    try:
        role = EmployeeRoleCRUD.update_role(db, role_id, role_data, updated_by=current_user.username)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        return role
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


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a role (soft delete)"""
    try:
        success = EmployeeRoleCRUD.delete_role(db, role_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
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
# PAGE PERMISSION ENDPOINTS
# ============================================================================

@router.post("/page-permissions", response_model=PagePermissionResponse, status_code=status.HTTP_201_CREATED)
def create_page_permission(
    page_data: PagePermissionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new page permission"""
    try:
        # Check if page name already exists
        existing_page = EmployeeRoleCRUD.get_page_permission_by_name(db, page_data.page_name)
        if existing_page:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page permission with this name already exists"
            )
        
        page = EmployeeRoleCRUD.create_page_permission(db, page_data, created_by=current_user.username)
        return page
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


@router.get("/page-permissions", response_model=List[PagePermissionResponse])
def get_page_permissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all page permissions with pagination"""
    try:
        if active_only:
            pages = EmployeeRoleCRUD.get_active_page_permissions(db)
        else:
            pages = EmployeeRoleCRUD.get_all_page_permissions(db, skip=skip, limit=limit)
        return pages
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


@router.get("/page-permissions/{page_id}", response_model=PagePermissionResponse)
def get_page_permission(
    page_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific page permission by ID"""
    try:
        page = EmployeeRoleCRUD.get_page_permission_by_id(db, page_id)
        if not page:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Page permission not found"
            )
        return page
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


@router.put("/page-permissions/{page_id}", response_model=PagePermissionResponse)
def update_page_permission(
    page_id: int,
    page_data: PagePermissionUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a page permission"""
    try:
        page = EmployeeRoleCRUD.update_page_permission(db, page_id, page_data, updated_by=current_user.username)
        if not page:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Page permission not found"
            )
        return page
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


@router.delete("/page-permissions/{page_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_page_permission(
    page_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a page permission (soft delete)"""
    try:
        success = EmployeeRoleCRUD.delete_page_permission(db, page_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Page permission not found"
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
# ROLE PERMISSION ENDPOINTS
# ============================================================================

@router.post("/role-permissions", response_model=RolePermissionResponse, status_code=status.HTTP_201_CREATED)
def create_role_permission(
    permission_data: RolePermissionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new role permission"""
    try:
        permission = EmployeeRoleCRUD.create_role_permission(db, permission_data, created_by=current_user.username)
        return permission
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


@router.get("/role-permissions", response_model=List[RolePermissionResponse])
def get_role_permissions(
    role_id: Optional[int] = Query(None),
    page_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get role permissions filtered by role_id or page_id"""
    try:
        if role_id:
            permissions = EmployeeRoleCRUD.get_role_permissions_by_role(db, role_id)
        elif page_id:
            permissions = EmployeeRoleCRUD.get_role_permissions_by_page(db, page_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either role_id or page_id must be provided"
            )
        return permissions
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


@router.put("/role-permissions/{permission_id}", response_model=RolePermissionResponse)
def update_role_permission(
    permission_id: int,
    permission_data: RolePermissionUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a role permission"""
    try:
        permission = EmployeeRoleCRUD.update_role_permission(db, permission_id, permission_data, updated_by=current_user.username)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role permission not found"
            )
        return permission
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


@router.delete("/role-permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a role permission"""
    try:
        success = EmployeeRoleCRUD.delete_role_permission(db, permission_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role permission not found"
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
# EMPLOYEE ENDPOINTS
# ============================================================================

@router.post("/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new employee"""
    try:
        # Check if username already exists
        existing_employee = EmployeeRoleCRUD.get_employee_by_username(db, employee_data.username)
        if existing_employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee with this username already exists"
            )
        
        # Check if email already exists
        existing_email = EmployeeRoleCRUD.get_employee_by_email(db, employee_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee with this email already exists"
            )
        
        # Check if phone already exists
        existing_phone = EmployeeRoleCRUD.get_employee_by_phone(db, employee_data.phone)
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee with this phone already exists"
            )
        
        employee = EmployeeRoleCRUD.create_employee(db, employee_data, created_by=current_user.username)
        return employee
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


@router.get("/employees", response_model=List[EmployeeResponse])
def get_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all employees with pagination"""
    try:
        if active_only:
            employees = EmployeeRoleCRUD.get_active_employees(db)
        else:
            employees = EmployeeRoleCRUD.get_all_employees(db, skip=skip, limit=limit)
        return employees
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


@router.get("/employees/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific employee by ID"""
    try:
        employee = EmployeeRoleCRUD.get_employee_by_id(db, employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        return employee
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


@router.put("/employees/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an employee"""
    try:
        employee = EmployeeRoleCRUD.update_employee(db, employee_id, employee_data, updated_by=current_user.username)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        return employee
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


@router.delete("/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete an employee (soft delete)"""
    try:
        success = EmployeeRoleCRUD.delete_employee(db, employee_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
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