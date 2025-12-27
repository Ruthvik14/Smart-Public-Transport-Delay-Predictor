from fastapi import APIRouter
from app.api import endpoints, endpoints_arrivals, endpoints_alerts, endpoints_admin

api_router = APIRouter()
api_router.include_router(endpoints.router, prefix="/v1", tags=["core"])
api_router.include_router(endpoints_alerts.router, prefix="/v1", tags=["alerts"])
api_router.include_router(endpoints_admin.router, prefix="/v1", tags=["admin"])
