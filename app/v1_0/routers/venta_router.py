from fastapi import APIRouter, HTTPException, Depends
from dependency_injector.wiring import inject, Provide

from app.app_containers import ApplicationContainer
from app.v1_0.schemas.venta_schema import VentaRequestDTO, VentaResponse
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

@router.get("/obtener/{venta_id}", response_model=VentaResponse)
@inject
async def obtener_venta(
    venta_id: int,
    venta_service=Depends(Provide[ApplicationContainer.api_container.venta_service])
):
    venta = await venta_service.obtener_venta(venta_id)
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta

@router.delete("/eliminar/{venta_id}", response_model=dict)
@inject
async def eliminar_venta(
    venta_id: int,
    venta_service=Depends(Provide[ApplicationContainer.api_container.venta_service])
):
    """
    Elimina una venta y todos sus registros relacionados (detalles, utilidades).
    También revierte el stock y saldos correspondientes.
    """
    eliminado = await venta_service.eliminar_venta(venta_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Venta no encontrada o no se pudo eliminar")

    return {"mensaje": f"Venta con ID {venta_id} eliminada correctamente"}
