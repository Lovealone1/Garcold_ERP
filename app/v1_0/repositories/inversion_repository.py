from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.v1_0.models import Inversion
from app.v1_0.repositories import BaseRepository
from app.v1_0.entities import InversionDTO


class InversionRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(Inversion, db)

    async def create_inversion(self, inversion_dto: InversionDTO) -> Inversion:
        inversion = Inversion(**inversion_dto.model_dump())
        return await self.create(inversion)

    async def get_by_nombre(self, nombre: str) -> list[Inversion]:
        result = await self.db.execute(
            select(Inversion).where(Inversion.nombre.ilike(f"%{nombre}%"))
        )
        return result.scalars().all()

    async def update_saldo(self, inversion_id: int, nuevo_saldo: float) -> Inversion | None:
        inversion = await self.get_by_id(inversion_id)
        if inversion:
            inversion.saldo = nuevo_saldo
            await self.db.commit()
            await self.db.refresh(inversion)
            return inversion
        return None
