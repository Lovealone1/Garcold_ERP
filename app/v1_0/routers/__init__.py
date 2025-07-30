from app.v1_0.routers.venta_router import router as venta_router
from app.v1_0.routers.compra_router import router as compra_router
from app.v1_0.routers.pago_venta_router import router as pago_venta_router

defined_routers = [
    venta_router,
    compra_router,
    pago_venta_router
]