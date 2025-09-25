from typing import Optional, List, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1_0.models import Proveedor
from app.v1_0.entities import ProveedorDTO
from .base_repository import BaseRepository


class ProveedorRepository(BaseRepository[Proveedor]):
    def __init__(self):
        super().__init__(Proveedor)

    async def create_proveedor(
        self,
        dto: ProveedorDTO,
        session: AsyncSession
    ) -> Proveedor:
        """Crea un nuevo Proveedor a partir del DTO y hace flush para asignar su ID."""
        proveedor = Proveedor(**dto.model_dump())
        await self.add(proveedor, session)
        return proveedor

    async def get_by_id(
        self,
        proveedor_id: int,
        session: AsyncSession
    ) -> Optional[Proveedor]:
        """Obtiene un Proveedor por su ID, o None si no existe."""
        return await super().get_by_id(proveedor_id, session)

    async def update_proveedor(
        self,
        proveedor_id: int,
        dto: ProveedorDTO,
        session: AsyncSession
    ) -> Optional[Proveedor]:
        """Actualiza solo los campos permitidos de un Proveedor existente según el DTO."""
        proveedor = await self.get_by_id(proveedor_id, session)
        if not proveedor:
            return None

        allowed_fields = {"nombre", "cc_nit", "correo", "celular", "direccion", "ciudad"}

        for field, value in dto.model_dump(exclude_unset=True).items():
            if field in allowed_fields:
                setattr(proveedor, field, value)

        await self.update(proveedor, session)
        return proveedor

    async def delete_proveedor(
        self,
        proveedor_id: int,
        session: AsyncSession
    ) -> bool:
        """Elimina un Proveedor dado su ID; retorna True si existía."""
        proveedor = await self.get_by_id(proveedor_id, session)
        if not proveedor:
            return False

        await self.delete(proveedor, session)
        return True

    async def list_paginated(
        self,
        offset: int,
        limit: int,
        session: AsyncSession
    ) -> Tuple[List[Proveedor], int]:
        """Lista paginada con total."""
        stmt = (
            select(Proveedor)
            .order_by(Proveedor.id.asc())
            .offset(offset)
            .limit(limit)
        )
        items = (await session.execute(stmt)).scalars().all()
        total = await session.scalar(select(func.count(Proveedor.id)))
        return items, int(total or 0)