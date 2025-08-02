# app/v1_0/routers/producto_router.py

from typing import List
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector.wiring import inject, Provide

from app.utils.database.db_connector import get_db
from app.app_containers import ApplicationContainer

from app.v1_0.entities import ProductoDTO
from app.v1_0.schemas.producto_schema import ProductoRequestDTO, ProductoListDTO
from app.v1_0.services.producto_service import ProductoService

router = APIRouter(prefix="/productos", tags=["Productos"])


@router.post(
    "/crear",
    response_model=ProductoListDTO,
    summary="Crea un nuevo producto"
)
@inject
async def crear_producto(
    request: ProductoRequestDTO,
    db: AsyncSession = Depends(get_db),
    producto_service= Depends(
        Provide[ApplicationContainer.api_container.producto_service]
    )
):
    # Construyo el DTO de entidad desde el request schema
    dto = ProductoDTO(**request.model_dump())
    creado = await producto_service.crear_producto(dto, db)
    return ProductoListDTO(
        id=creado.id,
        referencia=creado.referencia,
        descripcion=creado.descripcion,
        cantidad=creado.cantidad,
        precio_compra=creado.precio_compra,
        precio_venta=creado.precio_venta,
        activo=creado.activo,
        fecha_creacion=creado.fecha_creacion
    )


@router.get(
    "/",
    response_model=List[ProductoListDTO],
    summary="Lista productos paginados"
)
@inject
async def listar_productos(
    page: int = Query(1, ge=1, description="Número de página"),
    db: AsyncSession = Depends(get_db),
    producto_service= Depends(
        Provide[ApplicationContainer.api_container.producto_service]
    )
):
    return await producto_service.listar_productos(page, db)


@router.get(
    "/obtener/{referencia}",
    response_model=ProductoListDTO,
    summary="Obtiene un producto por su referencia"
)
@inject
async def obtener_producto(
    referencia: str,
    db: AsyncSession = Depends(get_db),
    producto_service= Depends(
        Provide[ApplicationContainer.api_container.producto_service]
    )
):
    prod = await producto_service.obtener_por_referencia(referencia, db)
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return ProductoListDTO(
        id=prod.id,
        referencia=prod.referencia,
        descripcion=prod.descripcion,
        cantidad=prod.cantidad,
        precio_compra=prod.precio_compra,
        precio_venta=prod.precio_venta,
        activo=prod.activo,
        fecha_creacion=prod.fecha_creacion
    )


@router.get(
    "/buscar",
    response_model=List[ProductoListDTO],
    summary="Busca productos por descripción"
)
@inject
async def buscar_productos(
    descripcion: str = Query(..., description="Texto a buscar en la descripción"),
    db: AsyncSession = Depends(get_db),
    producto_service= Depends(
        Provide[ApplicationContainer.api_container.producto_service]
    )
):
    resultados = await producto_service.obtener_por_descripcion(descripcion, db)
    return [
        ProductoListDTO(
            id=p.id,
            referencia=p.referencia,
            descripcion=p.descripcion,
            cantidad=p.cantidad,
            precio_compra=p.precio_compra,
            precio_venta=p.precio_venta,
            activo=p.activo,
            fecha_creacion=p.fecha_creacion
        )
        for p in resultados
    ]


@router.put(
    "/actualizar/{producto_id}",
    response_model=ProductoListDTO,
    summary="Actualiza un producto existente"
)
@inject
async def actualizar_producto(
    producto_id: int,
    request: ProductoRequestDTO,
    db: AsyncSession = Depends(get_db),
    producto_service= Depends(
        Provide[ApplicationContainer.api_container.producto_service]
    )
):
    dto = ProductoDTO(**request.model_dump())
    actualizado = await producto_service.actualizar_producto(producto_id, dto, db)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return ProductoListDTO(
        id=actualizado.id,
        referencia=actualizado.referencia,
        descripcion=actualizado.descripcion,
        cantidad=actualizado.cantidad,
        precio_compra=actualizado.precio_compra,
        precio_venta=actualizado.precio_venta,
        activo=actualizado.activo,
        fecha_creacion=actualizado.fecha_creacion
    )


@router.delete(
    "/eliminar/{producto_id}",
    response_model=dict,
    summary="Elimina un producto"
)
@inject
async def eliminar_producto(
    producto_id: int,
    db: AsyncSession = Depends(get_db),
    producto_service= Depends(
        Provide[ApplicationContainer.api_container.producto_service]
    )
):
    ok = await producto_service.eliminar_producto(producto_id, db)
    if not ok:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"mensaje": f"Producto con ID {producto_id} eliminado correctamente"}


@router.patch(
    "/cambiar-estado/{producto_id}",
    response_model=ProductoListDTO,
    summary="Activa o desactiva un producto"
)
@inject
async def cambiar_estado(
    producto_id: int,
    db: AsyncSession = Depends(get_db),
    producto_service= Depends(
        Provide[ApplicationContainer.api_container.producto_service]
    )
):
    mod = await producto_service.cambiar_estado(producto_id, db)
    if not mod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return ProductoListDTO(
        id=mod.id,
        referencia=mod.referencia,
        descripcion=mod.descripcion,
        cantidad=mod.cantidad,
        precio_compra=mod.precio_compra,
        precio_venta=mod.precio_venta,
        activo=mod.activo,
        fecha_creacion=mod.fecha_creacion
    )


@router.patch(
    "/{producto_id}/aumentar-stock",
    response_model=ProductoListDTO,
    summary="Aumenta el stock de un producto"
)
@inject
async def aumentar_stock(
    producto_id: int,
    cantidad: int = Body(..., embed=True, description="Cantidad a agregar"),
    db: AsyncSession = Depends(get_db),
    producto_service= Depends(
        Provide[ApplicationContainer.api_container.producto_service]
    )
):
    try:
        mod = await producto_service.aumentar_stock(producto_id, cantidad, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not mod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return ProductoListDTO(
        id=mod.id,
        referencia=mod.referencia,
        descripcion=mod.descripcion,
        cantidad=mod.cantidad,
        precio_compra=mod.precio_compra,
        precio_venta=mod.precio_venta,
        activo=mod.activo,
        fecha_creacion=mod.fecha_creacion
    )


@router.patch(
    "/{producto_id}/disminuir-stock",
    response_model=ProductoListDTO,
    summary="Disminuye el stock de un producto"
)
@inject
async def disminuir_stock(
    producto_id: int,
    cantidad: int = Body(..., embed=True, description="Cantidad a restar"),
    db: AsyncSession = Depends(get_db),
    producto_service= Depends(
        Provide[ApplicationContainer.api_container.producto_service]
    )
):
    try:
        mod = await producto_service.disminuir_stock(producto_id, cantidad, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not mod:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado o stock insuficiente"
        )
    return ProductoListDTO(
        id=mod.id,
        referencia=mod.referencia,
        descripcion=mod.descripcion,
        cantidad=mod.cantidad,
        precio_compra=mod.precio_compra,
        precio_venta=mod.precio_venta,
        activo=mod.activo,
        fecha_creacion=mod.fecha_creacion
    )
