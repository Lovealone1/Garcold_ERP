# app/v1_0/repositories/producto_repository.py

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1_0.models import Producto
from app.v1_0.entities import ProductoDTO
from .base_repository import BaseRepository

class ProductoRepository(BaseRepository[Producto]):
    def __init__(self):
        super().__init__(Producto)

    async def create_producto(
        self,
        dto: ProductoDTO,
        session: AsyncSession
    ) -> Producto:
        """
        Crea un nuevo Producto usando todos los campos del DTO,
        incluidos activo y fecha_creacion.
        """
        payload = dto.model_dump()


        producto = Producto(**payload)

        await self.add(producto, session)
        return producto

    async def get_by_id(
        self,
        producto_id: int,
        session: AsyncSession
    ) -> Optional[Producto]:
        """
        Recupera un Producto por su ID.
        """
        return await super().get_by_id(producto_id, session)

    async def get_by_referencia(
        self,
        referencia: str,
        session: AsyncSession
    ) -> Optional[Producto]:
        """
        Recupera un Producto por su referencia exacta.
        """
        stmt = select(Producto).where(Producto.referencia == referencia)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_descripcion(
        self,
        descripcion: str,
        session: AsyncSession
    ) -> List[Producto]:
        """
        Busca Productos cuya descripción contenga la cadena (case‑insensitive).
        """
        stmt = select(Producto).where(Producto.descripcion.ilike(f"%{descripcion}%"))
        result = await session.execute(stmt)
        return result.scalars().all()

    async def update_producto(
        self,
        producto_id: int,
        dto: ProductoDTO,
        session: AsyncSession
    ) -> Optional[Producto]:
        """
        Actualiza un Producto existente con los campos proporcionados en el DTO.
        """
        producto = await self.get_by_id(producto_id, session)
        if not producto:
            return None

        for field, value in dto.model_dump(exclude_unset=True).items():
            setattr(producto, field, value)

        await self.update(producto, session)
        return producto

    async def delete_producto(
        self,
        producto_id: int,
        session: AsyncSession
    ) -> bool:
        """
        Elimina un Producto dado su ID.
        """
        producto = await self.get_by_id(producto_id, session)
        if not producto:
            return False

        await self.delete(producto, session)
        return True

    async def toggle_estado(
        self,
        producto_id: int,
        session: AsyncSession
    ) -> Optional[Producto]:
        """
        Invierte el flag `activo` de un Producto.
        """
        producto = await self.get_by_id(producto_id, session)
        if not producto:
            return None

        producto.activo = not producto.activo
        await self.update(producto, session)
        return producto

    async def aumentar_cantidad(
        self,
        producto_id: int,
        cantidad: int,
        session: AsyncSession
    ) -> Optional[Producto]:
        """
        Incrementa la cantidad en inventario de un Producto.
        """
        producto = await self.get_by_id(producto_id, session)
        if not producto:
            return None

        producto.cantidad = (producto.cantidad or 0) + cantidad
        await self.update(producto, session)
        return producto

    async def disminuir_cantidad(
        self,
        producto_id: int,
        cantidad: int,
        session: AsyncSession
    ) -> Optional[Producto]:
        """
        Decrementa la cantidad en inventario de un Producto si hay stock suficiente.
        """
        producto = await self.get_by_id(producto_id, session)
        if not producto or (producto.cantidad or 0) < cantidad:
            return None

        producto.cantidad -= cantidad
        await self.update(producto, session)
        return producto

    async def list_paginated(
            self,
            offset: int,
            limit: int,
            session: AsyncSession
        ) -> List[Producto]:
            """
            Recupera todos los Productos paginados.
            """
            stmt = (
                select(Producto)
                .offset(offset)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return result.scalars().all()