from typing import Optional, List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1_0.models import DetalleUtilidad
from app.v1_0.entities import DetalleUtilidadDTO
from .base_repository import BaseRepository


class DetalleUtilidadRepository(BaseRepository[DetalleUtilidad]):
    def __init__(self):
        super().__init__(DetalleUtilidad)

    async def create_detalle(
        self,
        dto: DetalleUtilidadDTO,
        session: AsyncSession
    ) -> DetalleUtilidad:
        """
        Crea un DetalleUtilidad a partir del DTO y hace flush para asignar su ID.
        """
        detalle = DetalleUtilidad(**dto.model_dump())
        await self.add(detalle, session)
        return detalle

    async def get_by_venta(
        self,
        venta_id: int,
        session: AsyncSession
    ) -> List[DetalleUtilidad]:
        stmt = select(DetalleUtilidad).where(DetalleUtilidad.venta_id == venta_id)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def bulk_insert_detalles(
        self,
        dtos: List[DetalleUtilidadDTO],
        session: AsyncSession
    ) -> List[DetalleUtilidad]:
        """
        Inserta en lote múltiples DetalleUtilidad a partir de una lista de DTOs.
        """
        detalles = [
            DetalleUtilidad(**dto.model_dump(exclude={"total_utilidad"}))
            for dto in dtos
        ]
        session.add_all(detalles)
        await session.flush()
        return detalles

    async def delete_by_venta(
        self,
        venta_id: int,
        session: AsyncSession
    ) -> int:
        """
        Elimina todos los DetalleUtilidad asociados a la venta_id dada
        y retorna el número de filas eliminadas.
        """
        stmt = delete(DetalleUtilidad).where(DetalleUtilidad.venta_id == venta_id)
        result = await session.execute(stmt)
        await session.flush()
        return result.rowcount
