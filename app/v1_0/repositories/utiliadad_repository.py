from typing import Optional, List, Tuple
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1_0.models import Utilidad
from app.v1_0.entities import UtilidadDTO
from .base_repository import BaseRepository

class UtilidadRepository(BaseRepository[Utilidad]):
    def __init__(self):
        super().__init__(Utilidad)

    async def create_utilidad(
        self,
        dto: UtilidadDTO,
        session: AsyncSession
    ) -> Utilidad:
        """
        Crea una nueva Utilidad a partir del DTO y hace flush para asignar su ID.
        """
        utilidad = Utilidad(**dto.model_dump())
        await self.add(utilidad, session)
        return utilidad

    async def get_by_venta(
        self,
        venta_id: int,
        session: AsyncSession
    ) -> Optional[Utilidad]:
        """
        Recupera la Utilidad asociada a una venta, o None si no existe.
        """
        stmt = select(Utilidad).where(Utilidad.venta_id == venta_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_by_venta(
        self,
        venta_id: int,
        session: AsyncSession
    ) -> int:
        """
        Elimina todas las Utilidades asociadas a la venta_id dada.
        Retorna el número de filas eliminadas.
        """
        stmt = delete(Utilidad).where(Utilidad.venta_id == venta_id)
        result = await session.execute(stmt)
        await session.flush()
        return result.rowcount

    async def list_paginated(
        self,
        offset: int,
        limit: int,
        session: AsyncSession
    ) -> Tuple[List[Utilidad], int]:
        """
        Lista de Utilidades paginada con total.
        Retorna items y total de registros.
        """
        stmt = (
            select(Utilidad)
            .order_by(Utilidad.id.asc())
            .offset(offset)
            .limit(limit)
        )
        items = (await session.execute(stmt)).scalars().all()
        total = await session.scalar(select(func.count(Utilidad.id)))
        return items, int(total or 0)

    async def get_utilidad_by_venta_id(
        self,
        venta_id: int,
        session: AsyncSession
    ) -> Optional[Utilidad]:
        """
        Recupera la utilidad específica por venta_id.
        """
        stmt = select(Utilidad).where(Utilidad.venta_id == venta_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
