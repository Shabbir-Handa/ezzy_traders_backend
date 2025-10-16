"""
Ezzy Traders Backend - FastAPI Application
Main application entry point with database initialization and router registration
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime
from time_utils import format_datetime_ist
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from dependencies import engine
from db_helper.models import Base
from routers import employees, auth, door_attribute, customer_quotation


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
# Global response override to format datetimes in dd-mm-yyyy.h:m:s (IST)
class ISTJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        def convert(obj):
            if isinstance(obj, datetime):
                return format_datetime_ist(obj)
            if isinstance(obj, list):
                return [convert(i) for i in obj]
            if isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            return obj

        return super().render(convert(content))

app.default_response_class = ISTJSONResponse

# ============================================================================
# MIDDLEWARE
# ============================================================================

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# ROUTERS
# ============================================================================

app.include_router(auth.router)
app.include_router(employees.router)
app.include_router(door_attribute.router)
app.include_router(customer_quotation.router)


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
