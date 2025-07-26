from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Callable

from app.v1_0.models import Estado
from app.v1_0.repositories import BaseRepository


class EstadoRepository(BaseRepository[Estado]):
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        super().__init__(session_factory=session_factory, model_class=Estado)

    async def get_by_id(self, estado_id: int, session: AsyncSession | None = None) -> Estado | None:
        """
        Obtiene un estado por su ID.
        """
        session = session or await self.get_session()
        result = await session.execute(
            select(Estado).where(Estado.id == estado_id)
        )
        return result.scalar_one_or_none()

    async def get_by_nombre(self, nombre: str, session: AsyncSession | None = None) -> Estado | None:
        """
        Obtiene un estado por su nombre exacto.
        """
        session = session or await self.get_session()
        result = await session.execute(
            select(Estado).where(Estado.nombre == nombre)
        )
        return result.scalar_one_or_none()
