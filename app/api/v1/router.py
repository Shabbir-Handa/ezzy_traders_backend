"""
API v1 Router
Registers all endpoint sub-routers.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    door_types,
    services,
    service_groupings,
    units,
    customers,
    quotations,
    employees,
)

api_v1_router = APIRouter()

api_v1_router.include_router(auth.router)
api_v1_router.include_router(door_types.router)
api_v1_router.include_router(services.router)
api_v1_router.include_router(service_groupings.router)
api_v1_router.include_router(units.router)
api_v1_router.include_router(customers.router)
api_v1_router.include_router(quotations.router)
api_v1_router.include_router(employees.router)
