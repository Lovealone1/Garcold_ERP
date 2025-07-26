from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Callable, Optional

from app.v1_0.models import Utilidad
from app.v1_0.repositories import BaseRepository
from app.v1_0.entities import UtilidadDTO


class UtilidadRepository(BaseRepository):
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        super().__init__(session_factory, Utilidad)

    async def create_utilidad(self, utilidad_dto: UtilidadDTO, session: Optional[AsyncSession] = None) -> Utilidad:
        utilidad = Utilidad(**utilidad_dto.model_dump())
        return await self.create(utilidad, session=session)

    async def get_by_venta(self, venta_id: int, session: Optional[AsyncSession] = None) -> Utilidad | None:
        session = session or await self.get_session()
        result = await session.execute(
            select(Utilidad).where(Utilidad.venta_id == venta_id)
        )
        return result.scalar_one_or_none()

    async def delete_by_venta(self, venta_id: int, session: Optional[AsyncSession] = None) -> None:
        session = session or await self.get_session()
        await session.execute(
            delete(Utilidad).where(Utilidad.venta_id == venta_id)
        )
        await session.commit()
