"""
Authentication Router
Handles login, logout, and token management
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from dependencies import get_db, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from db_helper.employee_crud import EmployeeCRUD
from schemas.schemas import EmployeeLoginResponse

router = APIRouter(prefix="/api", tags=["Authentication"])


# ============================================================================
# LOGIN ENDPOINTS
# ============================================================================

@router.post("/login")
async def login(
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login, returns an access token
    """
    # Authenticate employee
    employee = EmployeeCRUD.authenticate_employee(db, username, password)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": employee.username}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/login-user", response_model=EmployeeLoginResponse)
async def login_user(
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    """
    Authenticate employee and return access token with role information
    """
    # Authenticate employee
    employee = EmployeeCRUD.authenticate_employee(db, username, password)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": employee.username}, expires_delta=access_token_expires
    )

    return EmployeeLoginResponse(
        username=employee.username,
        email=employee.email,
        access_token=access_token,
        token_type="bearer",
        role=employee.role
    )


# ============================================================================
# TOKEN VALIDATION ENDPOINTS
# ============================================================================

@router.get("/me")
async def get_current_user_info(
        current_user=Depends(get_current_user)
):
    """
    Get current authenticated user information
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "role": current_user.role
    }


@router.post("/refresh")
async def refresh_token(
        current_user=Depends(get_current_user)
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
        "token_type": "bearer"
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
