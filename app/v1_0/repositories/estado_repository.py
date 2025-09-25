from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.v1_0.models import Estado
from .base_repository import BaseRepository

class EstadoRepository(BaseRepository[Estado]):
    def __init__(self):
        super().__init__(Estado)

    async def get_by_id(
        self,
        estado_id: int,
        session: AsyncSession
    ) -> Optional[Estado]:
        """Recupera un Estado por su ID."""
        return await super().get_by_id(estado_id, session)

    async def get_by_nombre(
        self,
        nombre: str,
        session: AsyncSession
    ) -> Optional[Estado]:
        """
        Recupera un Estado por su nombre, ignorando mayúsculas/minúsculas.
        """
        stmt = select(Estado).where(
            func.lower(Estado.nombre) == nombre.lower()
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_estados(
        self,
        session: AsyncSession
    ) -> List[Estado]:
        """
        Retorna todos los Estados.
        """
        result = await session.execute(select(Estado).order_by(Estado.id.asc()))
        return list(result.scalars().all())
