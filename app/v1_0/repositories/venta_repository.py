from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Callable, Optional

from app.v1_0.models import Venta
from app.v1_0.repositories import BaseRepository
from app.v1_0.entities import VentaDTO

class VentaRepository(BaseRepository):
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        super().__init__(session_factory, Venta)

    async def create_venta(self, venta_dto: VentaDTO, session: Optional[AsyncSession] = None) -> Venta:
        venta = Venta(**venta_dto.model_dump())
        return await self.create(venta, session=session)

    async def get_by_id(self, venta_id: int, session: Optional[AsyncSession] = None) -> Venta | None:
        return await super().get_by_id(venta_id, session=session)

    async def get_all(self, session: Optional[AsyncSession] = None) -> list[Venta]:
        return await super().get_all(session=session)

    async def update_venta(self, venta_id: int, venta_dto: VentaDTO, session: Optional[AsyncSession] = None) -> Venta | None:
        session = session or await self.get_session()
        venta = await self.get_by_id(venta_id, session=session)
        if venta:
            for field, value in venta_dto.model_dump(exclude_unset=True).items():
                setattr(venta, field, value)
            await session.commit()
            await session.refresh(venta)
            return venta
        return None

    async def delete_venta(self, venta_id: int, session: Optional[AsyncSession] = None) -> bool:
        session = session or await self.get_session()
        venta = await self.get_by_id(venta_id, session=session)
        if venta:
            await self.delete(venta, session=session)
            return True
        return False

