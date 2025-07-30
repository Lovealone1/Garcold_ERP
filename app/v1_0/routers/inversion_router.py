# app/v1_0/routers/inversion_router.py

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector.wiring import inject, Provide

from app.utils.database.db_connector import get_db
from app.app_containers import ApplicationContainer
from app.v1_0.schemas.inversion_schema import InversionRequestDTO, InversionResponseDTO, InversionUpdateDTO
from app.v1_0.entities import InversionDTO

router = APIRouter(
    prefix="/inversiones",
    tags=["Inversiones"],
)

@router.post(
    "/crear",
    response_model=InversionResponseDTO,
    summary="Registra una nueva inversión"
)
@inject
async def crear_inversion(
    request: InversionRequestDTO,
    db: AsyncSession = Depends(get_db),
    inversion_service=Depends(Provide[ApplicationContainer.api_container.inversion_service])
):
    dto = InversionDTO(
        nombre=request.nombre,
        saldo=request.saldo,
        fecha_vencimiento=request.fecha_vencimiento
    )
    inv = await inversion_service.crear_inversion(dto, db=db)
    return InversionResponseDTO(
        id=inv.id,
        nombre=inv.nombre,
        saldo=inv.saldo,
        fecha_vencimiento=inv.fecha_vencimiento
    )


@router.get(
    "/{inversion_id}",
    response_model=InversionResponseDTO,
    summary="Obtiene una inversión por su ID"
)
@inject
async def obtener_inversion(
    inversion_id: int,
    db: AsyncSession = Depends(get_db),
    inversion_service=Depends(Provide[ApplicationContainer.api_container.inversion_service])
):
    inv = await inversion_service.obtener_inversion(inversion_id, db=db)
    return InversionResponseDTO(
        id=inv.id,
        nombre=inv.nombre,
        saldo=inv.saldo,
        fecha_vencimiento=inv.fecha_vencimiento 
    )

@router.get(
    "/",
    response_model=List[InversionResponseDTO],
    summary="Lista todas las inversiones"
)
@inject
async def listar_inversiones(
    db: AsyncSession = Depends(get_db),
    inversion_service=Depends(Provide[ApplicationContainer.api_container.inversion_service])
):
    inversiones = await inversion_service.listar_inversiones(db=db)
    return [
        InversionResponseDTO(
            id=i.id,
            nombre=i.nombre,
            saldo=i.saldo,
            fecha_vencimiento=i.fecha_vencimiento
        )
        for i in inversiones
    ]

@router.put(
    "/actualizar/{inversion_id}",
    response_model=InversionResponseDTO,
    summary="Actualiza el saldo de una inversión existente"
)
@inject
async def actualizar_inversion(
    inversion_id: int,
    request: InversionUpdateDTO,
    db: AsyncSession = Depends(get_db),
    inversion_service=Depends(Provide[ApplicationContainer.api_container.inversion_service])
):
    """
    Modifica únicamente el saldo de una inversión.
    """
    inv = await inversion_service.actualizar_saldo(
        inversion_id, request.saldo, db=db
    )
    return InversionResponseDTO(
        id=inv.id,
        nombre=inv.nombre,
        saldo=inv.saldo,
        fecha_vencimiento=inv.fecha_vencimiento
    )

@router.delete(
    "/eliminar/{inversion_id}",
    response_model=dict,
    summary="Elimina una inversión por su ID"
)
@inject
async def eliminar_inversion(
    inversion_id: int,
    db: AsyncSession = Depends(get_db),
    inversion_service=Depends(Provide[ApplicationContainer.api_container.inversion_service])
):
    """
    Borra una inversión y retorna un mensaje de éxito.
    """
    deleted = await inversion_service.eliminar_inversion(inversion_id, db=db)
    if not deleted:
        raise HTTPException(status_code=404, detail="Inversión no encontrada")
    return {"mensaje": f"Inversión con ID {inversion_id} eliminada correctamente"}
