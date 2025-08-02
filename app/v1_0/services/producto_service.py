from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from fastapi import HTTPException

from app.v1_0.repositories.producto_repository import ProductoRepository
from app.v1_0.entities import ProductoDTO
from app.v1_0.models import Producto
from app.v1_0.schemas.producto_schema import ProductoListDTO

PAGE_SIZE = 10

class ProductoService:
    def __init__(self, producto_repository: ProductoRepository):
        self.repository = producto_repository

    async def crear_producto(
        self,
        producto_dto: ProductoDTO,
        db: AsyncSession
    ) -> Producto:
        async with db.begin():
            existente = await self.repository.get_by_referencia(
                producto_dto.referencia,
                session=db
            )
            if existente:
                raise ValueError("Ya existe un producto con esa referencia.")
            return await self.repository.create_producto(producto_dto, session=db)

    async def obtener_por_referencia(
        self,
        referencia: str,
        session: AsyncSession
    ) -> Optional[Producto]:
        return await self.repository.get_by_referencia(referencia, session=session)

    async def obtener_por_descripcion(
        self,
        descripcion: str,
        session: AsyncSession
    ) -> List[Producto]:
        return await self.repository.get_by_descripcion(descripcion, session=session)

    async def actualizar_producto(
        self,
        producto_id: int,
        producto_dto: ProductoDTO,
        session: AsyncSession
    ) -> Optional[Producto]:
        return await self.repository.update_producto(producto_id, producto_dto, session=session)

    async def eliminar_producto(
        self,
        producto_id: int,
        session: AsyncSession
    ) -> bool:
        async with session.begin():
            return await self.repository.delete_producto(producto_id, session=session)

    async def cambiar_estado(
        self,
        producto_id: int,
        session: AsyncSession
    ) -> Optional[Producto]:
        async with session.begin():
            return await self.repository.toggle_estado(producto_id, session=session)

    async def aumentar_stock(
        self,
        producto_id: int,
        cantidad: int,
        session: AsyncSession
    ) -> Optional[Producto]:
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")
        async with session.begin():
            return await self.repository.aumentar_cantidad(producto_id, cantidad, session=session)

    async def disminuir_stock(
        self,
        producto_id: int,
        cantidad: int,
        session: AsyncSession
    ) -> Optional[Producto]:
        async with session.begin():
            if cantidad <= 0:
                raise ValueError("La cantidad debe ser mayor que cero.")
            producto = await self.repository.get_by_id(producto_id, session=session)
            if not producto:
                return None
            if (producto.cantidad or 0) < cantidad:
                raise ValueError("Stock insuficiente para realizar la operación.")
            
            return await self.repository.disminuir_cantidad(producto_id, cantidad, session=session)

    async def listar_productos(
        self,
        page: int,
        session: AsyncSession
    ) -> List[ProductoListDTO]:
        if page < 1:
            raise HTTPException(status_code=400, detail="page debe ser >= 1")

        offset = (page - 1) * PAGE_SIZE
        productos = await self.repository.list_paginated(offset, PAGE_SIZE, session=session)

        return [
            ProductoListDTO(
                id=p.id,
                referencia=p.referencia,
                descripcion=p.descripcion,
                cantidad=p.cantidad,
                precio_compra=p.precio_compra,
                precio_venta=p.precio_venta,
                activo=p.activo,
                fecha_creacion=p.fecha_creacion,
            )
            for p in productos
        ]
