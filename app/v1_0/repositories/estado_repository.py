# app/v1_0/repositories/estado_repository.py

from typing import Optional
from sqlalchemy import select
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
        """
        Recupera un Estado por su ID.
        """
        # Podemos usar el método genérico de BaseRepository:
        return await super().get_by_id(estado_id, session)

    async def get_by_nombre(
        self,
        nombre: str,
        session: AsyncSession
    ) -> Optional[Estado]:
        """
        Recupera un Estado por su nombre exacto.
        """
        stmt = select(Estado).where(Estado.nombre == nombre)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
