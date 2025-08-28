"""
Dependencies for FastAPI application
Database connection, authentication, and user management
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from jose import jwt
from passlib.context import CryptContext
from base import Base
from db_helper.models import Employee, Role, RolePermission, PagePermission
from schemas.schemas import TokenData

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

DATABASE_URL = "postgresql://postgres:1A58gW3HQ0VrZZsT@db.aqwiookdxlsskmznqkgy.supabase.co:5432/postgres"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ============================================================================
# PASSWORD HASHING
# ============================================================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

# ============================================================================
# JWT CONFIGURATION
# ============================================================================

SECRET_KEY = "your-secret-key-here-change-in-production"  # Change this in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login-form")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[TokenData]:
    """Verify JWT token and return token data"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return TokenData(username=username)
    except jwt.JWTError:
        return None

# ============================================================================
# DATABASE DEPENDENCIES
# ============================================================================

def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# AUTHENTICATION DEPENDENCIES
# ============================================================================

# OAuth2 scheme for Swagger docs authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# HTTP Bearer for existing authentication
security = HTTPBearer()

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[Session, Depends(get_db)]
) -> Employee:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verify_token(credentials.credentials)
    if token_data is None:
        raise credentials_exception
    
    user = db.query(Employee).filter(
        Employee.username == token_data.username,
        Employee.is_active == True
    ).first()
    
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: Annotated[Employee, Depends(get_current_user)]
) -> Employee:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# ============================================================================
# PERMISSION CHECKING
# ============================================================================

def check_permission(
    user: Employee,
    page_path: str,
    permission_type: str,
    db: Session
) -> bool:
    """Check if user has specific permission for a page"""
    if not user.role_id:
        return False
    
    # Get role permissions for the specific page
    permission = db.query(RolePermission).join(PagePermission).filter(
        RolePermission.role_id == user.role_id,
        PagePermission.page_path == page_path,
        RolePermission.is_active == True,
        PagePermission.is_active == True
    ).first()
    
    if not permission:
        return False
    
    # Check specific permission type
    if permission_type == "view":
        return permission.can_view
    elif permission_type == "create":
        return permission.can_create
    elif permission_type == "edit":
        return permission.can_edit
    elif permission_type == "delete":
        return permission.can_delete
    elif permission_type == "export":
        return permission.can_export
    elif permission_type == "import":
        return permission.can_import
    
    return False

def require_permission(permission_type: str):
    """Decorator to require specific permission"""
    def permission_dependency(
        current_user: Annotated[Employee, Depends(get_current_active_user)],
        db: Annotated[Session, Depends(get_db)]
    ):
        # This would need to be implemented based on the specific endpoint
        # For now, we'll just check if user is authenticated
        return current_user
    
    return permission_dependency

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_user_permissions(user: Employee, db: Session) -> dict:
    """Get all permissions for a user"""
    if not user.role_id:
        return {"pages": []}
    
    permissions = db.query(RolePermission).join(PagePermission).filter(
        RolePermission.role_id == user.role_id,
        RolePermission.is_active == True,
        PagePermission.is_active == True
    ).all()
    
    pages = []
    for perm in permissions:
        page_info = {
            "page_id": perm.page_id,
            "page_name": perm.page_permission.page_name,
            "page_path": perm.page_permission.page_path,
            "display_name": perm.page_permission.display_name,
            "permissions": {
                "can_view": perm.can_view,
                "can_create": perm.can_create,
                "can_edit": perm.can_edit,
                "can_delete": perm.can_delete,
                "can_export": perm.can_export,
                "can_import": perm.can_import
            }
        }
        pages.append(page_info)
    
    return {"pages": pages}
