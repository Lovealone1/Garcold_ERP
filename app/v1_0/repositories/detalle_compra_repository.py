from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.v1_0.models import DetalleCompra
from app.v1_0.repositories import BaseRepository
from app.v1_0.entities import DetalleCompraDTO

class DetalleCompraRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(DetalleCompra, db)

    async def create_detalle(self, detalle_dto: DetalleCompraDTO) -> DetalleCompra:
        detalle = DetalleCompra(**detalle_dto.model_dump())
        return await self.create(detalle)

    async def get_by_compra_id(self, compra_id: int) -> list[DetalleCompra]:
        result = await self.db.execute(
            select(DetalleCompra).where(DetalleCompra.compra_id == compra_id)
        )
        return result.scalars().all()

    async def update_detalle(self, detalle_id: int, detalle_dto: DetalleCompraDTO) -> DetalleCompra | None:
        detalle = await self.get_by_id(detalle_id)
        if detalle:
            for field, value in detalle_dto.model_dump(exclude_unset=True).items():
                setattr(detalle, field, value)
            await self.db.commit()
            await self.db.refresh(detalle)
            return detalle
        return None

    async def delete_detalle(self, detalle_id: int) -> bool:
        detalle = await self.get_by_id(detalle_id)
        if detalle:
            await self.delete(detalle)
            return True
        return False
