"""
Authentication Router
Handles login, logout, and token management
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from dependencies import get_db, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from db_helper.employee_role_crud import EmployeeRoleCRUD
from schemas.schemas import EmployeeLogin, EmployeeLoginResponse, UserPermissions

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ============================================================================
# LOGIN ENDPOINTS
# ============================================================================

@router.post("/login", response_model=EmployeeLoginResponse)
async def login(
    login_data: EmployeeLogin,
    db: Session = Depends(get_db)
):
    username = login_data.username
    password = login_data.password
    """
    Authenticate employee and return access token with permissions
    """
    # Authenticate employee
    employee = EmployeeRoleCRUD.authenticate_employee(db, username, password)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not employee.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive employee account"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": employee.username}, expires_delta=access_token_expires
    )
    
    # Get user permissions
    permissions = EmployeeRoleCRUD.get_user_permissions(db, employee)
    
    # Get role information
    role = None
    if employee.role:
        role = {
            "id": employee.role.id,
            "name": employee.role.name,
            "description": employee.role.description,
            "is_active": employee.role.is_active
        }
    
    return EmployeeLoginResponse(
        username=employee.username,
        email=employee.email,
        access_token=access_token,
        token_type="bearer",
        permissions=permissions,
        role=role
    )

@router.post("/login-form", response_model=EmployeeLoginResponse)
async def login_form(
    login_data: EmployeeLogin,
    db: Session = Depends(get_db)
):
    """
    Alternative login endpoint for form-based authentication
    """
    return await login(login_data=login_data, db=db)

# ============================================================================
# TOKEN VALIDATION ENDPOINTS
# ============================================================================

@router.get("/me", response_model=UserPermissions)
async def get_current_user_info(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user information and permissions
    """
    return EmployeeRoleCRUD.get_user_permissions_detailed(db, current_user)

@router.post("/refresh")
async def refresh_token(
    current_user = Depends(get_current_user)
):
    """
    Refresh access token for current user
    """
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

# ============================================================================
# LOGOUT ENDPOINTS
# ============================================================================

@router.post("/logout")
async def logout():
    """
    Logout endpoint (client should discard token)
    """
    return {"message": "Successfully logged out"}

# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@router.get("/status")
async def auth_status():
    """
    Check authentication service status
    """
    return {
        "status": "healthy",
        "service": "authentication",
        "token_expiry_minutes": ACCESS_TOKEN_EXPIRE_MINUTES
    }
