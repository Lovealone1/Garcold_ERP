from fastapi import APIRouter, HTTPException, Depends
from dependency_injector.wiring import inject, Provide

from app.app_containers import ApplicationContainer
from app.v1_0.schemas.compra_schema import CompraRequestDTO, CompraResponse
from app.v1_0.entities import CompraDTO

router = APIRouter(prefix="/compras", tags=["Compras"])

@router.post("/crear", response_model=CompraDTO)
@inject
async def crear_compra(
    request: CompraRequestDTO,
    compra_service=Depends(Provide[ApplicationContainer.api_container.compra_service])
):
    if not request.carrito:
        raise HTTPException(status_code=400, detail="El carrito no puede estar vacío")

    detalles = compra_service.construir_detalles(request.carrito)
    compra = await compra_service.registrar_compra(
        proveedor_id=request.proveedor_id,
        banco_id=request.banco_id,
        estado_id=request.estado_id,
        detalles=detalles
    )
    return compra

@router.get("/obtener/{compra_id}", response_model=CompraResponse)
@inject
async def obtener_compra(
    compra_id: int,
    compra_service=Depends(Provide[ApplicationContainer.api_container.compra_service])
):
    compra = await compra_service.obtener_compra(compra_id)
    if not compra:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    return compra

@router.delete("/eliminar/{compra_id}", response_model=dict)
@inject
async def eliminar_compra(
    compra_id: int,
    compra_service=Depends(Provide[ApplicationContainer.api_container.compra_service])
):
    """
    Elimina una compra y todos sus registros relacionados (detalles).
    También revierte el stock y saldos correspondientes.
    """
    eliminado = await compra_service.eliminar_compra(compra_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Compra no encontrada o no se pudo eliminar")

    return {"mensaje": f"Compra con ID {compra_id} eliminada correctamente"}
