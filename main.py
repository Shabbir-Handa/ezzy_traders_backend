"""
Ezzy Traders Backend - FastAPI Application
Main application entry point with database initialization and router registration
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from dependencies import engine
from base import Base
from routers import employee_role, auth
# from routers import door_attribute, customer_quotation

# ============================================================================
# APPLICATION LIFECYCLE
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    print("Starting Ezzy Traders Backend...")
    
    # Test database connection
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
    except SQLAlchemyError as e:
        print(f"❌ Database connection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )
    
    # Create tables
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/verified")
    except SQLAlchemyError as e:
        print(f"❌ Database table creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database table creation failed"
        )
    
    yield
    
    # Shutdown
    print("Shutting down Ezzy Traders Backend...")
    engine.dispose()

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="Ezzy Traders Backend",
    description="Backend API for Ezzy Traders door quotation system",
    version="1.0.0",
    lifespan=lifespan
)

# ============================================================================
# MIDDLEWARE
# ============================================================================

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# ROUTERS
# ============================================================================

# Authentication
app.include_router(
    auth.router,
    prefix="/api/v1",
    tags=["Authentication"]
)

# Employee and Role Management
app.include_router(
    employee_role.router,
    prefix="/api/v1",
    tags=["Employee & Role Management"]
)

# Door and Attribute Management
# app.include_router(
#     door_attribute.router,
#     prefix="/api/v1",
#     tags=["Door & Attribute Management"]
# )

# Customer and Quotation Management
# app.include_router(
#     customer_quotation.router,
#     prefix="/api/v1",
#     tags=["Customer & Quotation Management"]
# )

# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Ezzy Traders Backend API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": "2024-01-01T00:00:00Z"  # You can use datetime.now() here
        }
    except SQLAlchemyError:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "timestamp": "2024-01-01T00:00:00Z"
        }

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request, exc):
    """Handle database errors"""
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Database operation failed"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
