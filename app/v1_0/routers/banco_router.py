from typing import Dict, List
from fastapi import APIRouter, HTTPException, Depends, Body, status
from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector.wiring import inject, Provide

from app.utils.database.db_connector import get_db
from app.app_containers import ApplicationContainer

from app.v1_0.entities import BancoDTO
from app.v1_0.schemas.banco_schema import BancoCreateSchema
from app.v1_0.services.banco_service import BancoService

router = APIRouter(prefix="/bancos", tags=["Bancos"])


@router.post(
    "/crear",
    response_model=BancoDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Crea un nuevo banco",
)
@inject
async def crear_banco(
    request: BancoCreateSchema,
    db: AsyncSession = Depends(get_db),
    banco_service: BancoService = Depends(
        Provide[ApplicationContainer.api_container.banco_service]
    ),
):
    try:
        creado = await banco_service.create_banco(request, db)  # type: ignore[arg-type]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return BancoDTO(
        id=creado.id,
        nombre=creado.nombre,
        saldo=creado.saldo,
        fecha_creacion=creado.fecha_creacion,
        fecha_actualizacion=creado.fecha_actualizacion,
    )


@router.get(
    "/",
    response_model=List[BancoDTO],
    summary="Lista todos los bancos",
)
@inject
async def listar_bancos(
    db: AsyncSession = Depends(get_db),
    banco_service: BancoService = Depends(
        Provide[ApplicationContainer.api_container.banco_service]
    ),
) -> List[BancoDTO]:
    bancos = await banco_service.get_all_bancos(db)
    return [
        BancoDTO(
            id=b.id,
            nombre=b.nombre,
            saldo=b.saldo,
            fecha_creacion=b.fecha_creacion,
            fecha_actualizacion=b.fecha_actualizacion,
        )
        for b in bancos
    ]


@router.patch(
    "/saldo/{banco_id}",
    response_model=BancoDTO,
    summary="Actualiza sólo el saldo de un banco",
)
@inject
async def actualizar_saldo_banco(
    banco_id: int,
    nuevo_saldo: float = Body(..., embed=True, description="Nuevo saldo"),
    db: AsyncSession = Depends(get_db),
    banco_service: BancoService = Depends(
        Provide[ApplicationContainer.api_container.banco_service]
    ),
):
    banco = await banco_service.update_saldo(banco_id, nuevo_saldo, db)
    if not banco:
        raise HTTPException(status_code=404, detail="Banco no encontrado")

    return BancoDTO(
        id=banco.id,
        nombre=banco.nombre,
        saldo=banco.saldo,
        fecha_creacion=banco.fecha_creacion,
        fecha_actualizacion=banco.fecha_actualizacion,
    )


@router.delete(
    "/eliminar/{banco_id}",
    response_model=Dict[str, str],
    summary="Elimina un banco",
)
@inject
async def eliminar_banco(
    banco_id: int,
    db: AsyncSession = Depends(get_db),
    banco_service: BancoService = Depends(
        Provide[ApplicationContainer.api_container.banco_service]
    ),
):
    try:
        ok = await banco_service.delete_banco(banco_id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not ok:
        raise HTTPException(status_code=404, detail="Banco no encontrado")

    return {"mensaje": f"Banco con ID {banco_id} eliminado correctamente"}
