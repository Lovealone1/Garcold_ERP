from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Callable

from app.v1_0.models import DetalleUtilidad
from app.v1_0.repositories import BaseRepository
from app.v1_0.entities import DetalleUtilidadDTO


class DetalleUtilidadRepository(BaseRepository[DetalleUtilidad]):
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        super().__init__(session_factory=session_factory, model_class=DetalleUtilidad)

    async def create_detalle(self, detalle_dto: DetalleUtilidadDTO, session: AsyncSession | None = None) -> DetalleUtilidad:
        detalle = DetalleUtilidad(**detalle_dto.model_dump())
        return await self.create(detalle, session=session)

    async def get_by_venta(self, venta_id: int, session: AsyncSession | None = None) -> list[DetalleUtilidad]:
        session = session or await self.get_session()
        result = await session.execute(
            select(DetalleUtilidad).where(DetalleUtilidad.venta_id == venta_id)
        )
        return result.scalars().all()

    async def bulk_insert_detalles(self, detalles_dto: list[DetalleUtilidadDTO], session: AsyncSession | None = None) -> list[DetalleUtilidad]:
        """
        Inserta múltiples detalles de utilidad en una sola operación.
        """
        session = session or await self.get_session()
        detalles = [DetalleUtilidad(**dto.model_dump(exclude={"total_utilidad"})) for dto in detalles_dto]
        session.add_all(detalles)
        await session.commit()
        for detalle in detalles:
            await session.refresh(detalle)
        return detalles
