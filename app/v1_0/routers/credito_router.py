# app/v1_0/routers/credito_router.py

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector.wiring import inject, Provide

from app.utils.database.db_connector import get_db
from app.app_containers import ApplicationContainer
from app.v1_0.schemas.credito_schema import CreditoRequestDTO, CreditoResponseDTO
from app.v1_0.entities import CreditoDTO

router = APIRouter(
    prefix="/creditos",
    tags=["Créditos"],
)

@router.post(
    "/crear",
    response_model=CreditoResponseDTO,
    summary="Registra un nuevo crédito"
)
@inject
async def crear_credito(
    request: CreditoRequestDTO,
    db: AsyncSession = Depends(get_db),
    credito_service=Depends(Provide[ApplicationContainer.api_container.credito_service])
):
    """
    Crea un crédito con nombre y monto inicial.
    """
    dto = CreditoDTO(**request.dict())
    credito = await credito_service.crear_credito(dto, db=db)
    return CreditoResponseDTO(
        id=credito.id,
        nombre=credito.nombre,
        monto=credito.monto
    )

@router.get(
    "/{credito_id}",
    response_model=CreditoResponseDTO,
    summary="Obtiene un crédito por su ID"
)
@inject
async def obtener_credito(
    credito_id: int,
    db: AsyncSession = Depends(get_db),
    credito_service=Depends(Provide[ApplicationContainer.api_container.credito_service])
):
    """
    Devuelve los datos de un crédito existente.
    """
    credito = await credito_service.obtener_credito(credito_id, db=db)
    return CreditoResponseDTO(
        id=credito.id,
        nombre=credito.nombre,
        monto=credito.monto
    )

@router.get(
    "/",
    response_model=List[CreditoResponseDTO],
    summary="Lista todos los créditos"
)
@inject
async def listar_creditos(
    db: AsyncSession = Depends(get_db),
    credito_service=Depends(Provide[ApplicationContainer.api_container.credito_service])
):
    """
    Recupera todos los créditos registrados.
    """
    creditos = await credito_service.listar_creditos(db=db)
    return [
        CreditoResponseDTO(id=c.id, nombre=c.nombre, monto=c.monto)
        for c in creditos
    ]

@router.put(
    "/actualizar/{credito_id}",
    response_model=CreditoResponseDTO,
    summary="Actualiza el monto de un crédito existente"
)
@inject
async def actualizar_credito(
    credito_id: int,
    request: CreditoRequestDTO,
    db: AsyncSession = Depends(get_db),
    credito_service=Depends(Provide[ApplicationContainer.api_container.credito_service])
):
    """
    Modifica únicamente el monto de un crédito.
    """
    credito = await credito_service.actualizar_monto(
        credito_id, request.monto, db=db
    )
    return CreditoResponseDTO(
        id=credito.id,
        nombre=credito.nombre,
        monto=credito.monto
    )

@router.delete(
    "/eliminar/{credito_id}",
    response_model=dict,
    summary="Elimina un crédito por su ID"
)
@inject
async def eliminar_credito(
    credito_id: int,
    db: AsyncSession = Depends(get_db),
    credito_service=Depends(Provide[ApplicationContainer.api_container.credito_service])
):
    """
    Borra un crédito y retorna un mensaje de éxito.
    """
    deleted = await credito_service.eliminar_credito(credito_id, db=db)
    if not deleted:
        raise HTTPException(status_code=404, detail="Crédito no encontrado")
    return {"mensaje": f"Crédito con ID {credito_id} eliminado correctamente"}
