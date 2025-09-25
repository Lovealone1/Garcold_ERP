from math import ceil
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1_0.repositories.producto_repository import ProductoRepository
from app.v1_0.entities import ProductoDTO, ProductoListDTO, ProductosPageDTO
from app.v1_0.models import Producto

PAGE_SIZE = 10

class ProductoService:
    def __init__(self, producto_repository: ProductoRepository):
        self.repository = producto_repository

    async def crear_producto(
        self,
        producto_dto: ProductoDTO,
        db: AsyncSession
    ) -> Producto:
        # Validaciones simples
        if producto_dto.precio_compra < 0 or producto_dto.precio_venta < 0:
            raise ValueError("Los precios no pueden ser negativos.")
        if producto_dto.cantidad is not None and producto_dto.cantidad < 0:
            raise ValueError("La cantidad no puede ser negativa.")

        async with db.begin():
            # Unicidad por referencia (si aplica en tu modelo)
            if hasattr(self.repository, "get_by_referencia"):
                existente = await self.repository.get_by_referencia(
                    producto_dto.referencia, session=db
                )
                if existente:
                    raise ValueError("Ya existe un producto con esa referencia.")
            return await self.repository.create_producto(producto_dto, session=db)

    async def actualizar_producto(
        self,
        producto_id: int,
        producto_dto: ProductoDTO,
        db: AsyncSession
    ) -> Producto:
        if producto_dto.precio_compra is not None and producto_dto.precio_compra < 0:
            raise ValueError("precio_compra inválido")
        if producto_dto.precio_venta is not None and producto_dto.precio_venta < 0:
            raise ValueError("precio_venta inválido")
        if producto_dto.cantidad is not None and producto_dto.cantidad < 0:
            raise ValueError("cantidad inválida")

        async with db.begin():
            updated = await self.repository.update_producto(producto_id, producto_dto, session=db)
            if not updated:
                raise ValueError("Producto no encontrado")
            return updated

    async def eliminar_producto(
        self,
        producto_id: int,
        db: AsyncSession
    ) -> bool:
        async with db.begin():
            prod = await self.repository.get_by_id(producto_id, session=db)
            if not prod:
                raise ValueError("Producto no encontrado")
            return await self.repository.delete_producto(producto_id, session=db)

    async def cambiar_estado(
        self,
        producto_id: int,
        db: AsyncSession
    ) -> Producto:
        async with db.begin():
            prod = await self.repository.toggle_estado(producto_id, session=db)
            if not prod:
                raise ValueError("Producto no encontrado")
            return prod

    async def aumentar_stock(
        self,
        producto_id: int,
        cantidad: int,
        db: AsyncSession
    ) -> Producto:
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")
        async with db.begin():
            prod = await self.repository.aumentar_cantidad(producto_id, cantidad, session=db)
            if not prod:
                raise ValueError("Producto no encontrado")
            return prod

    async def disminuir_stock(
        self,
        producto_id: int,
        cantidad: int,
        db: AsyncSession
    ) -> Producto:
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")
        async with db.begin():
            # Validar existencia/stock antes de operar
            prod = await self.repository.get_by_id(producto_id, session=db)
            if not prod:
                raise ValueError("Producto no encontrado")
            if (prod.cantidad or 0) < cantidad:
                raise ValueError("Stock insuficiente para realizar la operación.")
            prod = await self.repository.disminuir_cantidad(producto_id, cantidad, session=db)
            if not prod:
                raise ValueError("Producto no encontrado o stock insuficiente")
            return prod

    async def listar_productos(
        self,
        page: int,
        db: AsyncSession
    ) -> ProductosPageDTO:
        offset = (page - 1) * PAGE_SIZE

        async with db.begin():
            # Items paginados
            items_models: List[Producto] = await self.repository.list_paginated(
                offset, PAGE_SIZE, session=db
            )
            # Total
            total = await db.scalar(select(func.count(Producto.id))) or 0

        total = int(total)
        total_pages = max(1, ceil(total / PAGE_SIZE)) if total else 1

        items = [
            ProductoListDTO(
                id=p.id,
                referencia=p.referencia,
                descripcion=p.descripcion,
                cantidad=p.cantidad or 0,
                precio_compra=p.precio_compra,
                precio_venta=p.precio_venta,
                activo=bool(p.activo),
                fecha_creacion=p.fecha_creacion,
            )
            for p in items_models
        ]

        return ProductosPageDTO(
            items=items,
            page=page,
            page_size=PAGE_SIZE,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )

    async def obtener_por_id(
            self,
            producto_id: int,
            db: AsyncSession
        ) -> Optional[Producto]:
            """Retorna el producto por ID o None."""
            async with db.begin():
                return await self.repository.get_by_id(producto_id, session=db)
            
    async def listar_productos_all(
    self,
    db: AsyncSession
    ) -> List[ProductoListDTO]:
        """
        Lista TODOS los productos (sin paginación).
        """
        async with db.begin():
            items_models: List[Producto] = await self.repository.list_productos(session=db)

        return [
            ProductoListDTO(
                id=p.id,
                referencia=p.referencia,
                descripcion=p.descripcion,
                cantidad=p.cantidad or 0,
                precio_compra=p.precio_compra,
                precio_venta=p.precio_venta,
                activo=bool(p.activo),
                fecha_creacion=p.fecha_creacion,
            )
            for p in items_models
        ]