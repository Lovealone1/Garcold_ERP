from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Callable, Optional, List

from app.v1_0.models import DetalleCompra
from app.v1_0.repositories import BaseRepository
from app.v1_0.entities import DetalleCompraDTO

class DetalleCompraRepository(BaseRepository):
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        super().__init__(session_factory, DetalleCompra)

    async def create_detalle(self, detalle_dto: DetalleCompraDTO, session: Optional[AsyncSession] = None) -> DetalleCompra:
        session = session or await self.get_session()
        detalle = DetalleCompra(**detalle_dto.model_dump())
        session.add(detalle)
        await session.commit()
        await session.refresh(detalle)
        return detalle

    async def get_by_compra_id(self, compra_id: int, session: Optional[AsyncSession] = None) -> list[DetalleCompra]:
        session = session or await self.get_session()
        result = await session.execute(
            select(DetalleCompra).where(DetalleCompra.compra_id == compra_id)
        )
        return result.scalars().all()

    async def update_detalle(self, detalle_id: int, detalle_dto: DetalleCompraDTO, session: Optional[AsyncSession] = None) -> DetalleCompra | None:
        session = session or await self.get_session()
        detalle = await self.get_by_id(detalle_id, session=session)
        if detalle:
            for field, value in detalle_dto.model_dump(exclude_unset=True).items():
                setattr(detalle, field, value)
            await session.commit()
            await session.refresh(detalle)
            return detalle
        return None

    async def delete_detalle(self, detalle_id: int, session: Optional[AsyncSession] = None) -> bool:
        session = session or await self.get_session()
        detalle = await self.get_by_id(detalle_id, session=session)
        if detalle:
            await self.delete(detalle, session=session)
            return True
        return False

    async def bulk_insert_detalles(self, detalles: List[DetalleCompraDTO], session: Optional[AsyncSession] = None) -> List[DetalleCompra]:
            session = session or await self.get_session()
            objects = [DetalleCompra(**d.model_dump(exclude={"total"})) for d in detalles]
            session.add_all(objects)
            await session.commit()
            for obj in objects:
                await session.refresh(obj)
            return objects