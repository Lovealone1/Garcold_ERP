from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.v1_0.models import Gasto
from app.v1_0.repositories import BaseRepository
from app.v1_0.entities import GastoDTO  


class GastoRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(Gasto, db)

    async def create_gasto(self, gasto_dto: GastoDTO) -> Gasto:
        gasto = Gasto(**gasto_dto.model_dump())
        return await self.create(gasto)

    async def get_by_fecha(self, fecha: str) -> list[Gasto]:
        result = await self.db.execute(
            select(Gasto).where(Gasto.fecha_gasto == fecha)
        )
        return result.scalars().all()

    async def get_by_categoria(self, categoria_id: int) -> list[Gasto]:
        result = await self.db.execute(
            select(Gasto).where(Gasto.categoria_gasto_id == categoria_id)
        )
        return result.scalars().all()

    async def delete_gasto(self, gasto_id: int) -> bool:
        gasto = await self.get_by_id(gasto_id)
        if gasto:
            await self.delete(gasto)
            return True
        return False
