from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.v1_0.models import Estado
from app.v1_0.repositories import BaseRepository

class EstadoRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(Estado, db)

    async def get_by_id(self, estado_id: int) -> Estado | None:
        """
        Obtiene un estado por su ID.

        Args:
            estado_id (int): ID del estado.

        Returns:
            Estado si existe, de lo contrario None.
        """
        result = await self.db.execute(
            select(Estado).where(Estado.id == estado_id)
        )
        return result.scalar_one_or_none()

    async def get_by_nombre(self, nombre: str) -> Estado | None:
        """
        Obtiene un estado por su nombre exacto.

        Args:
            nombre (str): Nombre del estado.

        Returns:
            Estado si existe, de lo contrario None.
        """
        result = await self.db.execute(
            select(Estado).where(Estado.nombre == nombre)
        )
        return result.scalar_one_or_none()
