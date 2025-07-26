from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Callable, Optional

from app.v1_0.models import DetalleVenta
from app.v1_0.repositories import BaseRepository
from app.v1_0.entities import DetalleVentaDTO


class DetalleVentaRepository(BaseRepository):
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        super().__init__(session_factory, DetalleVenta)

    async def create_detalle(self, detalle_dto: DetalleVentaDTO, session: Optional[AsyncSession] = None) -> DetalleVenta:
        session = session or await self.get_session()
        detalle = DetalleVenta(**detalle_dto.model_dump())
        session.add(detalle)
        await session.commit()
        await session.refresh(detalle)
        return detalle

    async def get_by_venta_id(self, venta_id: int, session: Optional[AsyncSession] = None) -> List[DetalleVenta]:
        session = session or await self.get_session()
        result = await session.execute(
            select(DetalleVenta).where(DetalleVenta.venta_id == venta_id)
        )
        return result.scalars().all()

    async def delete_detalle(self, detalle_id: int, session: Optional[AsyncSession] = None) -> bool:
        session = session or await self.get_session()
        detalle = await session.get(DetalleVenta, detalle_id)
        if detalle:
            await session.delete(detalle)
            await session.commit()
            return True
        return False

    async def update_detalle(self, detalle_id: int, detalle_dto: DetalleVentaDTO, session: Optional[AsyncSession] = None) -> DetalleVenta | None:
        session = session or await self.get_session()
        detalle = await session.get(DetalleVenta, detalle_id)
        if detalle:
            for field, value in detalle_dto.model_dump(exclude_unset=True).items():
                setattr(detalle, field, value)
            await session.commit()
            await session.refresh(detalle)
            return detalle
        return None

    async def bulk_insert_detalles(self, detalles: List[DetalleVentaDTO], session: Optional[AsyncSession] = None) -> List[DetalleVenta]:
        session = session or await self.get_session()
        objects = [DetalleVenta(**d.model_dump(exclude={"total"})) for d in detalles]
        session.add_all(objects)
        await session.commit()
        for obj in objects:
            await session.refresh(obj)
        return objects

    async def delete_by_venta(self, venta_id: int, session: Optional[AsyncSession] = None) -> None:
        session = session or await self.get_session()
        await session.execute(
            delete(DetalleVenta).where(DetalleVenta.venta_id == venta_id)
        )
        await session.commit()
