from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.v1_0.models import Transaccion
from app.v1_0.repositories import BaseRepository
from app.v1_0.entities import TransaccionDTO


class TransaccionRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(Transaccion, db)

    async def create_transaccion(self, transaccion_dto: TransaccionDTO) -> Transaccion:
        transaccion = Transaccion(**transaccion_dto.model_dump())
        return await self.create(transaccion)

    async def get_by_banco(self, banco_id: int) -> list[Transaccion]:
        result = await self.db.execute(
            select(Transaccion).where(Transaccion.banco_id == banco_id)
        )
        return result.scalars().all()

    async def get_by_tipo(self, tipo_id: int) -> list[Transaccion]:
        result = await self.db.execute(
            select(Transaccion).where(Transaccion.tipo_id == tipo_id)
        )
        return result.scalars().all()
