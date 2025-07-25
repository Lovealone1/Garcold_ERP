from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Callable

from app.v1_0.models import DetalleVenta
from app.v1_0.repositories import BaseRepository
from app.v1_0.entities import DetalleVentaDTO

class DetalleVentaRepository(BaseRepository):
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        self._session_factory = session_factory

    async def create_detalle(self, detalle_dto: DetalleVentaDTO) -> DetalleVenta:
        async with self._session_factory() as session:
            detalle = DetalleVenta(**detalle_dto.model_dump())
            session.add(detalle)
            await session.commit()
            await session.refresh(detalle)
            return detalle

    async def get_by_venta_id(self, venta_id: int) -> list[DetalleVenta]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(DetalleVenta).where(DetalleVenta.venta_id == venta_id)
            )
            return result.scalars().all()

    async def delete_detalle(self, detalle_id: int) -> bool:
        async with self._session_factory() as session:
            detalle = await session.get(DetalleVenta, detalle_id)
            if detalle:
                await session.delete(detalle)
                await session.commit()
                return True
            return False

    async def update_detalle(self, detalle_id: int, detalle_dto: DetalleVentaDTO) -> DetalleVenta | None:
        async with self._session_factory() as session:
            detalle = await session.get(DetalleVenta, detalle_id)
            if detalle:
                for field, value in detalle_dto.model_dump(exclude_unset=True).items():
                    setattr(detalle, field, value)
                await session.commit()
                await session.refresh(detalle)
                return detalle
            return None

    async def bulk_insert_detalles(self, detalles: List[DetalleVentaDTO]) -> List[DetalleVenta]:
        async with self._session_factory() as session:
            objects = [DetalleVenta(**d.model_dump(exclude={"total"})) for d in detalles]
            session.add_all(objects)
            await session.commit()
            for obj in objects:
                await session.refresh(obj)
            return objects
