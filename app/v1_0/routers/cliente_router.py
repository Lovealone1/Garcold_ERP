from typing import Dict, List
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector.wiring import inject, Provide

from app.utils.database.db_connector import get_db
from app.app_containers import ApplicationContainer

# Solo DTOs de entidades para salida. Schemas sólo para entrada.
from app.v1_0.entities import ClienteDTO, ClienteListDTO, ClientesPageDTO, ListClienteDTO
from app.v1_0.schemas.cliente_schema import ClienteRequestDTO
from app.v1_0.services.cliente_service import ClienteService

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.post(
    "/crear",
    response_model=ClienteDTO,
    summary="Crea un nuevo cliente",
)
@inject
async def crear_cliente(
    request: ClienteRequestDTO,
    db: AsyncSession = Depends(get_db),
    cliente_service: ClienteService = Depends(
        Provide[ApplicationContainer.api_container.cliente_service]
    ),
):
    dto = ClienteDTO(**request.model_dump())
    try:
        creado = await cliente_service.crear_cliente(dto, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Retornar el DTO con todos los campos, incluso los opcionales
    return ClienteDTO(
        id=creado.id,
        cc_nit=creado.cc_nit,
        nombre=creado.nombre,
        direccion=creado.direccion,
        ciudad=creado.ciudad,
        celular=creado.celular,
        correo=creado.correo,
        fecha_creacion=creado.fecha_creacion,
        saldo=creado.saldo,
    )


@router.get(
    "/",
    response_model=ClientesPageDTO,
    summary="Lista clientes paginados",
)
@inject
async def listar_clientes(
    page: int = Query(1, ge=1, description="Número de página"),
    db: AsyncSession = Depends(get_db),
    cliente_service: ClienteService = Depends(
        Provide[ApplicationContainer.api_container.cliente_service]
    ),
) -> ClientesPageDTO:
    return await cliente_service.listar_clientes(page=page, db=db)


@router.get(
    "/all",
    response_model=List[ListClienteDTO],
    summary="Lista todos los clientes (id, nombre) sin paginar",
)
@inject
async def listar_clientes_all(
    db: AsyncSession = Depends(get_db),
    cliente_service: ClienteService = Depends(
        Provide[ApplicationContainer.api_container.cliente_service]
    ),
) -> List[ListClienteDTO]:
    return await cliente_service.listar_clientes_all(db=db)

@router.get(
    "/{cliente_id}",
    response_model=ClienteListDTO,
    summary="Obtiene un cliente por ID",
)
@inject
async def obtener_cliente_por_id(
    cliente_id: int,
    db: AsyncSession = Depends(get_db),
    cliente_service: ClienteService = Depends(
        Provide[ApplicationContainer.api_container.cliente_service]
    ),
):
    cliente = await cliente_service.obtener_por_id(cliente_id, db)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    return ClienteListDTO(
        id=cliente.id,
        nombre=cliente.nombre,
        cc_nit=cliente.cc_nit,
        correo=cliente.correo,
        celular=cliente.celular,
        direccion=cliente.direccion,
        ciudad=cliente.ciudad,
        saldo=cliente.saldo,
        fecha_creacion=cliente.fecha_creacion,
    )


@router.put(
    "/actualizar/{cliente_id}",
    response_model=ClienteDTO,
    summary="Actualiza un cliente existente",
)
@inject
async def actualizar_cliente(
    cliente_id: int,
    request: ClienteRequestDTO,
    db: AsyncSession = Depends(get_db),
    cliente_service: ClienteService = Depends(
        Provide[ApplicationContainer.api_container.cliente_service]
    ),
):
    dto = ClienteDTO(**request.model_dump())
    try:
        actualizado = await cliente_service.actualizar_cliente(cliente_id, dto, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return ClienteDTO(
        cc_nit=actualizado.cc_nit,
        nombre=actualizado.nombre,
        direccion=actualizado.direccion,  
        ciudad=actualizado.ciudad,
        celular=actualizado.celular,
        correo=actualizado.correo,
        saldo=actualizado.saldo,
        fecha_creacion=actualizado.fecha_creacion,
    )


@router.patch(
    "/saldo/{cliente_id}",
    response_model=ClienteListDTO,
    summary="Actualiza sólo el saldo de un cliente",
)
@inject
async def actualizar_saldo_cliente(
    cliente_id: int,
    nuevo_saldo: float = Body(..., embed=True, description="Nuevo saldo"),
    db: AsyncSession = Depends(get_db),
    cliente_service: ClienteService = Depends(
        Provide[ApplicationContainer.api_container.cliente_service]
    ),
):
    try:
        cliente = await cliente_service.actualizar_saldo(cliente_id, nuevo_saldo, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return ClienteListDTO(
        id=cliente.id,
        nombre=cliente.nombre,
        cc_nit=cliente.cc_nit,
        correo=cliente.correo,
        celular=cliente.celular,
        ciudad=cliente.ciudad,
        saldo=cliente.saldo,
    )


@router.delete(
    "/eliminar/{cliente_id}",
    response_model=Dict[str, str],
    summary="Elimina un cliente",
)
@inject
async def eliminar_cliente(
    cliente_id: int,
    db: AsyncSession = Depends(get_db),
    cliente_service: ClienteService = Depends(
        Provide[ApplicationContainer.api_container.cliente_service]
    ),
):
    try:
        await cliente_service.eliminar_cliente(cliente_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"mensaje": f"Cliente con ID {cliente_id} eliminado correctamente"}
