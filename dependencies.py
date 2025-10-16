"""
Dependencies for FastAPI application
Database connection, authentication, and user management
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from jose import jwt, JWTError
from passlib.context import CryptContext
from db_helper.models import Employee
from schemas.schemas import TokenData

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

try:
    DATABASE_URL = "postgresql://postgres:TrA+ZPrfhwjLa7i@db.vanonpimvxobfypishpo.supabase.co:5432/postgres"
    engine = create_engine(DATABASE_URL)
except:
    DATABASE_URL = "postgresql://postgres.vanonpimvxobfypishpo:TrA+ZPrfhwjLa7i@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"
    engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ============================================================================
# PASSWORD HASHING
# ============================================================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")


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
ACCESS_TOKEN_EXPIRE_MINUTES = 300


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
async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> Employee:
    """Get current authenticated user from JWT token"""
    return await get_user(token=token, db=db)


async def get_user(
        token: Depends(oauth2_scheme),
        db: Session = Depends(get_db),
) -> Employee:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(Employee).filter(
        Employee.username == username,
    ).first()
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
        current_user: Annotated[Employee, Depends(get_current_user)]
) -> Employee:
    """Get current active user"""
    return current_user
