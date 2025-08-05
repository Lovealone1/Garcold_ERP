from typing import List
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector.wiring import inject, Provide

from app.utils.database.db_connector import get_db
from app.app_containers import ApplicationContainer

from app.v1_0.entities import ClienteDTO
from app.v1_0.schemas.cliente_schema import ClienteRequestDTO, ClienteListDTO
from app.v1_0.services.cliente_service import ClienteService

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.post(
    "/crear",
    response_model=ClienteListDTO,
    summary="Crea un nuevo cliente"
)
@inject
async def crear_cliente(
    request: ClienteRequestDTO,
    db: AsyncSession = Depends(get_db),
    cliente_service: ClienteService = Depends(
        Provide[ApplicationContainer.api_container.cliente_service]
    )
):
    dto = ClienteDTO(**request.model_dump())
    try:
        creado = await cliente_service.crear_cliente(dto, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ClienteListDTO(
        id=creado.id,
        nombre=creado.nombre,
        cc_nit=creado.cc_nit,
        correo=creado.correo,
        celular=creado.celular,
        saldo=creado.saldo,
        fecha_creacion=creado.fecha_creacion
    )


@router.get(
    "/",
    response_model=List[ClienteListDTO],
    summary="Lista clientes paginados"
)
@inject
async def listar_clientes(
    page: int = Query(1, ge=1, description="Número de página"),
    db: AsyncSession = Depends(get_db),
    cliente_service: ClienteService = Depends(
        Provide[ApplicationContainer.api_container.cliente_service]
    )
):
    clientes = await cliente_service.listar_clientes(page, db)
    return [
        ClienteListDTO(
            id=c.id,
            nombre=c.nombre,
            cc_nit=c.cc_nit,
            correo=c.correo,
            celular=c.celular,
            saldo=c.saldo,
            fecha_creacion=c.fecha_creacion
        )
        for c in clientes
    ]


@router.get(
    "/obtener/{cc_nit}",
    response_model=ClienteListDTO,
    summary="Obtiene un cliente por CC/NIT"
)
@inject
async def obtener_cliente(
    cc_nit: str,
    db: AsyncSession = Depends(get_db),
    cliente_service: ClienteService = Depends(
        Provide[ApplicationContainer.api_container.cliente_service]
    )
):
    cliente = await cliente_service.obtener_por_cc_nit(cc_nit, db)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return ClienteListDTO(
        id=cliente.id,
        nombre=cliente.nombre,
        cc_nit=cliente.cc_nit,
        correo=cliente.correo,
        celular=cliente.celular,
        saldo=cliente.saldo,
        fecha_creacion=cliente.fecha_creacion
    )


@router.get(
    "/buscar",
    response_model=List[ClienteListDTO],
    summary="Busca clientes por nombre"
)
@inject
async def buscar_clientes(
    nombre: str = Query(..., description="Texto a buscar en el nombre"),
    db: AsyncSession = Depends(get_db),
    cliente_service: ClienteService = Depends(
        Provide[ApplicationContainer.api_container.cliente_service]
    )
):
    resultados = await cliente_service.obtener_por_nombre(nombre, db)
    return [
        ClienteListDTO(
            id=c.id,
            nombre=c.nombre,
            cc_nit=c.cc_nit,
            correo=c.correo,
            celular=c.celular,
            saldo=c.saldo,
            fecha_creacion=c.fecha_creacion
        )
        for c in resultados
    ]


@router.put(
    "/actualizar/{cliente_id}",
    response_model=ClienteListDTO,
    summary="Actualiza un cliente existente"
)
@inject
async def actualizar_cliente(
    cliente_id: int,
    request: ClienteRequestDTO,
    db: AsyncSession = Depends(get_db),
    cliente_service: ClienteService = Depends(
        Provide[ApplicationContainer.api_container.cliente_service]
    )
):
    dto = ClienteDTO(**request.model_dump())
    try:
        actualizado = await cliente_service.actualizar_cliente(cliente_id, dto, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return ClienteListDTO(
        id=actualizado.id,
        nombre=actualizado.nombre,
        cc_nit=actualizado.cc_nit,
        correo=actualizado.correo,
        celular=actualizado.celular,
        saldo=actualizado.saldo,
        fecha_creacion=actualizado.fecha_creacion
    )


@router.delete(
    "/eliminar/{cliente_id}",
    response_model=dict,
    summary="Elimina un cliente"
)
@inject
async def eliminar_cliente(
    cliente_id: int,
    db: AsyncSession = Depends(get_db),
    cliente_service: ClienteService = Depends(
        Provide[ApplicationContainer.api_container.cliente_service]
    )
):
    try:
        await cliente_service.eliminar_cliente(cliente_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"mensaje": f"Cliente con ID {cliente_id} eliminado correctamente"}
