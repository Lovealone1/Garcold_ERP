from typing import Dict
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector.wiring import inject, Provide

from app.utils.database.db_connector import get_db
from app.app_containers import ApplicationContainer

# DTOs de entidades para salida. Schemas sólo para entrada.
from app.v1_0.entities import ProveedorDTO, ProveedorListDTO, ProveedoresPageDTO
from app.v1_0.schemas.proveedor_schema import ProveedorRequestDTO
from app.v1_0.services.proveedor_service import ProveedorService

router = APIRouter(prefix="/proveedores", tags=["Proveedores"])


@router.post(
    "/crear",
    response_model=ProveedorDTO,
    summary="Crea un nuevo proveedor",
)
@inject
async def crear_proveedor(
    request: ProveedorRequestDTO,
    db: AsyncSession = Depends(get_db),
    proveedor_service: ProveedorService = Depends(
        Provide[ApplicationContainer.api_container.proveedor_service]
    ),
):
    dto = ProveedorDTO(**request.model_dump())
    try:
        creado = await proveedor_service.crear_proveedor(dto, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return ProveedorDTO(
        id=creado.id,
        cc_nit=creado.cc_nit,
        nombre=creado.nombre,
        direccion=creado.direccion,
        ciudad=creado.ciudad,
        celular=creado.celular,
        correo=creado.correo,
        fecha_creacion=creado.fecha_creacion,
    )


@router.get(
    "/",
    response_model=ProveedoresPageDTO,
    summary="Lista proveedores paginados",
)
@inject
async def listar_proveedores(
    page: int = Query(1, ge=1, description="Número de página"),
    db: AsyncSession = Depends(get_db),
    proveedor_service: ProveedorService = Depends(
        Provide[ApplicationContainer.api_container.proveedor_service]
    ),
) -> ProveedoresPageDTO:
    return await proveedor_service.listar_proveedores(page=page, db=db)


@router.get(
    "/{proveedor_id}",
    response_model=ProveedorListDTO,
    summary="Obtiene un proveedor por ID",
)
@inject
async def obtener_proveedor_por_id(
    proveedor_id: int,
    db: AsyncSession = Depends(get_db),
    proveedor_service: ProveedorService = Depends(
        Provide[ApplicationContainer.api_container.proveedor_service]
    ),
):
    proveedor = await proveedor_service.obtener_por_id(proveedor_id, db)
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    return ProveedorListDTO(
        id=proveedor.id,
        nombre=proveedor.nombre,
        cc_nit=proveedor.cc_nit,
        correo=proveedor.correo,
        celular=proveedor.celular,
        direccion=proveedor.direccion,
        ciudad=proveedor.ciudad,
        fecha_creacion=proveedor.fecha_creacion,
    )


@router.put(
    "/actualizar/{proveedor_id}",
    response_model=ProveedorDTO,
    summary="Actualiza un proveedor existente",
)
@inject
async def actualizar_proveedor(
    proveedor_id: int,
    request: ProveedorRequestDTO,
    db: AsyncSession = Depends(get_db),
    proveedor_service: ProveedorService = Depends(
        Provide[ApplicationContainer.api_container.proveedor_service]
    ),
):
    dto = ProveedorDTO(**request.model_dump())
    try:
        actualizado = await proveedor_service.actualizar_proveedor(proveedor_id, dto, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return ProveedorDTO(
        cc_nit=actualizado.cc_nit,
        nombre=actualizado.nombre,
        direccion=actualizado.direccion,
        ciudad=actualizado.ciudad,
        celular=actualizado.celular,
        correo=actualizado.correo,
        fecha_creacion=actualizado.fecha_creacion,
    )


@router.delete(
    "/eliminar/{proveedor_id}",
    response_model=Dict[str, str],
    summary="Elimina un proveedor",
)
@inject
async def eliminar_proveedor(
    proveedor_id: int,
    db: AsyncSession = Depends(get_db),
    proveedor_service: ProveedorService = Depends(
        Provide[ApplicationContainer.api_container.proveedor_service]
    ),
):
    try:
        await proveedor_service.eliminar_proveedor(proveedor_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"mensaje": f"Proveedor con ID {proveedor_id} eliminado correctamente"}
