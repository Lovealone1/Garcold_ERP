# app/v1_0/routers/compra_router.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector.wiring import inject, Provide

from app.utils.database.db_connector import get_db
from app.app_containers import ApplicationContainer
from app.v1_0.schemas.compra_schema import CompraResponse, CompraRequestDTO
from app.v1_0.entities.compraDTO import CompraDTO

router = APIRouter(prefix="/compras", tags=["Compras"])

@router.post(
    "/crear",
    response_model=CompraResponse,
    summary="Registra una nueva compra"
)
@inject
async def crear_compra(
    request: CompraRequestDTO ,
    db: AsyncSession = Depends(get_db),
    compra_service=Depends(Provide[ApplicationContainer.api_container.compra_service])
):
    if not request.carrito:
        raise HTTPException(status_code=400, detail="El carrito no puede estar vacío")

    detalles = compra_service.construir_detalles(request.carrito)
    compra = await compra_service.registrar_compra(
        proveedor_id=request.proveedor_id,
        banco_id=request.banco_id,
        estado_id=request.estado_id,
        detalles=detalles,
        db=db
    )
    return compra

@router.get(
    "/obtener/{compra_id}",
    response_model=CompraResponse,
    summary="Obtiene una compra por su ID"
)
@inject
async def obtener_compra(
    compra_id: int,
    db: AsyncSession = Depends(get_db),
    compra_service=Depends(Provide[ApplicationContainer.api_container.compra_service])
):
    return await compra_service.obtener_compra(compra_id, db=db)

@router.delete(
    "/eliminar/{compra_id}",
    response_model=dict,
    summary="Elimina una compra y revierte inventario y saldos"
)
@inject
async def eliminar_compra(
    compra_id: int,
    db: AsyncSession = Depends(get_db),
    compra_service=Depends(Provide[ApplicationContainer.api_container.compra_service])
):
    await compra_service.eliminar_compra(compra_id, db=db)
    return {"mensaje": f"Compra con ID {compra_id} eliminada correctamente"}
