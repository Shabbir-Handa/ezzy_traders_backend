"""
API v1 Router
Registers all endpoint sub-routers.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, door_services, customer_quotations, employees

api_v1_router = APIRouter()

api_v1_router.include_router(auth.router)
api_v1_router.include_router(door_services.router)
api_v1_router.include_router(customer_quotations.router)
api_v1_router.include_router(employees.router)
