"""
Authentication Endpoints
Handles login, token refresh, logout, and health check.
Routes contain NO business logic — all logic delegated to services.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.security import create_access_token, get_current_user
from app.db.session import get_db
from app.services.employee_service import EmployeeService
from app.schemas.employee import EmployeeLoginResponse

router = APIRouter(prefix="", tags=["Authentication"])


@router.post("/login")
async def login(
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    """OAuth2 compatible token login"""
    employee = EmployeeService.authenticate_employee(db, username, password)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": employee.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login-user", response_model=EmployeeLoginResponse)
async def login_user(
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    """Authenticate employee and return access token with role information"""
    employee = EmployeeService.authenticate_employee(db, username, password)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

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


@router.get("/me")
async def get_current_user_info(current_user=Depends(get_current_user)):
    """Get current authenticated user information"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "role": current_user.role
    }


@router.post("/refresh")
async def refresh_token(current_user=Depends(get_current_user)):
    """Refresh access token"""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout():
    """Logout (client should discard token)"""
    return {"message": "Successfully logged out"}


@router.get("/status")
async def auth_status():
    """Check authentication service status"""
    return {
        "status": "healthy",
        "service": "authentication",
        "token_expiry_minutes": ACCESS_TOKEN_EXPIRE_MINUTES
    }
