"""
Application Configuration
Centralized configuration using environment variables with sensible defaults.
"""

import os


# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres.nszmthzgfkosckdhaboz:TrA+ZPrfhwjLa7i@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"
)

# ============================================================================
# JWT CONFIGURATION
# ============================================================================

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "300"))
