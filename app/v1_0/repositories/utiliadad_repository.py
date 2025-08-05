# app/v1_0/repositories/utilidad_repository.py

from typing import Optional, List
from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

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
    ) -> List[Utilidad]:
        """
        Recupera todas las Utilidades paginadas.
        """
        stmt = (
            select(Utilidad)
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def list_by_rango_paginated(
        self,
        fecha_inicio: datetime,
        fecha_fin: datetime,
        offset: int,
        limit: int,
        session: AsyncSession
    ) -> List[Utilidad]:
        """
        Recupera Utilidades entre fecha_inicio y fecha_fin, paginadas.
        """
        stmt = (
            select(Utilidad)
            .where(
                and_(
                    Utilidad.fecha >= fecha_inicio,
                    Utilidad.fecha <= fecha_fin
                )
            )
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()