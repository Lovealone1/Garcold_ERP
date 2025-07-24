from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.v1_0.models import DetalleUtilidad
from app.v1_0.repositories import BaseRepository
from app.v1_0.entities import DetalleUtilidadDTO

class DetalleUtilidadRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(DetalleUtilidad, db)

    async def create_detalle(self, detalle_dto: DetalleUtilidadDTO) -> DetalleUtilidad:
        detalle = DetalleUtilidad(**detalle_dto.model_dump())
        return await self.create(detalle)

    async def get_by_venta(self, venta_id: int) -> list[DetalleUtilidad]:
        result = await self.db.execute(
            select(DetalleUtilidad).where(DetalleUtilidad.venta_id == venta_id)
        )
        return result.scalars().all()