from fastapi import APIRouter
from app.v1_0.routers.venta_router import venta_router

router = APIRouter(prefix="/v1", tags=["v1"])

router.include_router(venta_router.router)
