from fastapi import APIRouter, HTTPException, Depends
from dependency_injector.wiring import inject, Provide
from app.app_containers import ApplicationContainer
from app.v1_0.schemas.venta_schema import VentaRequestDTO
from app.v1_0.entities import VentaDTO

router = APIRouter(prefix="/ventas", tags=["Ventas"])

@router.post("/crear", response_model=VentaDTO)
@inject
async def crear_venta(
    request: VentaRequestDTO,
    venta_service=Depends(Provide[ApplicationContainer.api_container.venta_service])
):
    if not request.carrito:
        raise HTTPException(status_code=400, detail="El carrito no puede estar vacío")

    detalles = venta_service.agregar_detalle_venta(request.carrito)
    venta = await venta_service.finalizar_venta(
        cliente_id=request.cliente_id,
        banco_id=request.banco_id,
        estado_id=request.estado_id,
        detalles=detalles
    )
    return venta
