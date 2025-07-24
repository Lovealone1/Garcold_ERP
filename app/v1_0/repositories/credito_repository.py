from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.v1_0.models import Credito
from app.v1_0.repositories import BaseRepository
from app.v1_0.entities import CreditoDTO


class CreditoRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(Credito, db)

    async def create_credito(self, credito_dto: CreditoDTO) -> Credito:
        credito = Credito(**credito_dto.model_dump())
        return await self.create(credito)

    async def get_by_nombre(self, nombre: str) -> list[Credito]:
        result = await self.db.execute(
            select(Credito).where(Credito.nombre.ilike(f"%{nombre}%"))
        )
        return result.scalars().all()

    async def update_monto(self, credito_id: int, nuevo_monto: float) -> Credito | None:
        credito = await self.get_by_id(credito_id)
        if credito:
            credito.monto = nuevo_monto
            await self.db.commit()
            await self.db.refresh(credito)
            return credito
        return None
