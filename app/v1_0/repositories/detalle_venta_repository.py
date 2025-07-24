from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.v1_0.models import DetalleVenta
from app.v1_0.repositories import BaseRepository
from app.v1_0.entities import DetalleVentaDTO

class DetalleVentaRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(DetalleVenta, db)

    async def create_detalle(self, detalle_dto: DetalleVentaDTO) -> DetalleVenta:
        detalle = DetalleVenta(**detalle_dto.model_dump())
        return await self.create(detalle)

    async def get_by_venta_id(self, venta_id: int) -> list[DetalleVenta]:
        result = await self.db.execute(
            select(DetalleVenta).where(DetalleVenta.venta_id == venta_id)
        )
        return result.scalars().all()

    async def delete_detalle(self, detalle_id: int) -> bool:
        detalle = await self.get_by_id(detalle_id)
        if detalle:
            await self.delete(detalle)
            return True
        return False

    async def update_detalle(self, detalle_id: int, detalle_dto: DetalleVentaDTO) -> DetalleVenta | None:
        detalle = await self.get_by_id(detalle_id)
        if detalle:
            for field, value in detalle_dto.model_dump(exclude_unset=True).items():
                setattr(detalle, field, value)
            await self.db.commit()
            await self.db.refresh(detalle)
            return detalle
        return None

    async def bulk_insert_detalles(self, detalles: List[DetalleVentaDTO]) -> None:
        """
        Inserta múltiples detalles de venta en una sola operación.
        """
        objects = [DetalleVenta(**d.model_dump()) for d in detalles]
        self.db.add_all(objects)
        await self.db.commit()