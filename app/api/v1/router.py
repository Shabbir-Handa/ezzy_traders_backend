"""
API v1 Router
Aggregates all endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, employees, door_attributes, customer_quotations

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router)
router.include_router(employees.router)
router.include_router(door_attributes.router)
router.include_router(customer_quotations.router)
