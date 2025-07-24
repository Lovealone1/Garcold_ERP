from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.v1_0.models import Compra
from app.v1_0.repositories import BaseRepository
from app.v1_0.entities import CompraDTO

class CompraRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(Compra, db)

    async def create_compra(self, compra_dto: CompraDTO) -> Compra:
        compra = Compra(**compra_dto.model_dump())
        return await self.create(compra)

    async def get_by_proveedor(self, proveedor_id: int) -> list[Compra]:
        result = await self.db.execute(
            select(Compra).where(Compra.proveedor_id == proveedor_id)
        )
        return result.scalars().all()

    async def update_compra(self, compra_id: int, compra_dto: CompraDTO) -> Compra | None:
        compra = await self.get_by_id(compra_id)
        if compra:
            for field, value in compra_dto.model_dump(exclude_unset=True).items():
                setattr(compra, field, value)
            await self.db.commit()
            await self.db.refresh(compra)
            return compra
        return None

    async def delete_compra(self, compra_id: int) -> bool:
        compra = await self.get_by_id(compra_id)
        if compra:
            await self.delete(compra)
            return True
        return False
