from typing import List
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector.wiring import inject, Provide

from app.utils.database.db_connector import get_db
from app.app_containers import ApplicationContainer

from app.v1_0.entities import ProveedorDTO
from app.v1_0.schemas.proveedor_schema import ProveedorRequestDTO, ProveedorListDTO
from app.v1_0.services.proveedor_service import ProveedorService

router = APIRouter(prefix="/proveedores", tags=["Proveedores"])


@router.post(
    "/crear",
    response_model=ProveedorListDTO,
    summary="Crea un nuevo proveedor"
)
@inject
async def crear_proveedor(
    request: ProveedorRequestDTO,
    db: AsyncSession = Depends(get_db),
    service: ProveedorService = Depends(
        Provide[ApplicationContainer.api_container.proveedor_service]
    )
):
    dto = ProveedorDTO(**request.model_dump())
    try:
        creado = await service.crear_proveedor(dto, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ProveedorListDTO(
        id=creado.id,
        cc_nit=creado.cc_nit,
        nombre=creado.nombre,
        direccion=creado.direccion,
        ciudad=creado.ciudad,
        celular=creado.celular,
        correo=creado.correo,
        fecha_creacion=creado.fecha_creacion
    )


@router.get(
    "/",
    response_model=List[ProveedorListDTO],
    summary="Lista proveedores paginados"
)
@inject
async def listar_proveedores(
    page: int = Query(1, ge=1, description="Número de página"),
    db: AsyncSession = Depends(get_db),
    service: ProveedorService = Depends(
        Provide[ApplicationContainer.api_container.proveedor_service]
    )
):
    try:
        lista = await service.listar_proveedores(page, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return [
        ProveedorListDTO(
            id=p.id,
            cc_nit=p.cc_nit,
            nombre=p.nombre,
            direccion=p.direccion,
            ciudad=p.ciudad,
            celular=p.celular,
            correo=p.correo,
            fecha_creacion=p.fecha_creacion
        )
        for p in lista
    ]


@router.get(
    "/obtener/{cc_nit}",
    response_model=ProveedorListDTO,
    summary="Obtiene un proveedor por CC/NIT"
)
@inject
async def obtener_proveedor(
    cc_nit: str,
    db: AsyncSession = Depends(get_db),
    service: ProveedorService = Depends(
        Provide[ApplicationContainer.api_container.proveedor_service]
    )
):
    prov = await service.obtener_por_cc_nit(cc_nit, db)
    if not prov:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return ProveedorListDTO(
        id=prov.id,
        cc_nit=prov.cc_nit,
        nombre=prov.nombre,
        direccion=prov.direccion,
        ciudad=prov.ciudad,
        celular=prov.celular,
        correo=prov.correo,
        fecha_creacion=prov.fecha_creacion
    )


@router.get(
    "/buscar",
    response_model=List[ProveedorListDTO],
    summary="Busca proveedores por nombre"
)
@inject
async def buscar_proveedores(
    nombre: str = Query(..., description="Texto a buscar en el nombre"),
    db: AsyncSession = Depends(get_db),
    service: ProveedorService = Depends(
        Provide[ApplicationContainer.api_container.proveedor_service]
    )
):
    resultados = await service.obtener_por_nombre(nombre, db)
    return [
        ProveedorListDTO(
            id=p.id,
            cc_nit=p.cc_nit,
            nombre=p.nombre,
            direccion=p.direccion,
            ciudad=p.ciudad,
            celular=p.celular,
            correo=p.correo,
            fecha_creacion=p.fecha_creacion
        )
        for p in resultados
    ]


@router.put(
    "/actualizar/{proveedor_id}",
    response_model=ProveedorListDTO,
    summary="Actualiza un proveedor existente"
)
@inject
async def actualizar_proveedor(
    proveedor_id: int,
    request: ProveedorRequestDTO,
    db: AsyncSession = Depends(get_db),
    service: ProveedorService = Depends(
        Provide[ApplicationContainer.api_container.proveedor_service]
    )
):
    dto = ProveedorDTO(**request.model_dump())
    try:
        updated = await service.actualizar_proveedor(proveedor_id, dto, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return ProveedorListDTO(
        id=updated.id,
        cc_nit=updated.cc_nit,
        nombre=updated.nombre,
        direccion=updated.direccion,
        ciudad=updated.ciudad,
        celular=updated.celular,
        correo=updated.correo,
        fecha_creacion=updated.fecha_creacion
    )


@router.delete(
    "/eliminar/{proveedor_id}",
    response_model=dict,
    summary="Elimina un proveedor"
)
@inject
async def eliminar_proveedor(
    proveedor_id: int,
    db: AsyncSession = Depends(get_db),
    service: ProveedorService = Depends(
        Provide[ApplicationContainer.api_container.proveedor_service]
    )
):
    try:
        await service.eliminar_proveedor(proveedor_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"mensaje": f"Proveedor con ID {proveedor_id} eliminado correctamente"}
