from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.v1_0.models import Utilidad
from app.v1_0.repositories import BaseRepository
from app.v1_0.entities import UtilidadDTO


class UtilidadRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(Utilidad, db)

    async def create_utilidad(self, utilidad_dto: UtilidadDTO) -> Utilidad:
        utilidad = Utilidad(**utilidad_dto.model_dump())
        return await self.create(utilidad)

    async def get_by_venta(self, venta_id: int) -> Utilidad | None:
        result = await self.db.execute(
            select(Utilidad).where(Utilidad.venta_id == venta_id)
        )
        return result.scalar_one_or_none()