from app.v1_0.routers.venta_router import router as venta_router
from app.v1_0.routers.compra_router import router as compra_router
from app.v1_0.routers.pago_venta_router import router as pago_venta_router
from app.v1_0.routers.pago_compra_router import router as pago_compra_router
from app.v1_0.routers.gasto_router import router as gasto_router
from app.v1_0.routers.credito_router import router as credito_router
from app.v1_0.routers.inversion_router import router as inversion_router    
from app.v1_0.routers.transaccion_router import router as transaccion_router
from app.v1_0.routers.producto_router import router as producto_router
from app.v1_0.routers.cliente_router import router as cliente_router
from app.v1_0.routers.proveedor_router import router as proveedor_router
from app.v1_0.routers.utilidad_router import router as utilidad_router
from app.v1_0.routers.auth_router import router as auth_router
defined_routers = [
    venta_router,
    compra_router,
    pago_venta_router,
    pago_compra_router,
    gasto_router,
    credito_router,
    inversion_router,
    transaccion_router,
    producto_router,
    cliente_router,
    proveedor_router,
    utilidad_router, 
    auth_router
]