from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.v1_0.repositories.estado_repository import EstadoRepository
from app.v1_0.entities import EstadoDTO


class EstadoService:
    def __init__(self, estado_repository: EstadoRepository):
        self.estado_repository = estado_repository

    async def listar_estados(self, db: AsyncSession) -> List[EstadoDTO]:
        """
        Retorna todos los estados registrados, mapeados a DTO.

        Args:
            db (AsyncSession): Sesión de base de datos.

        Returns:
            List[EstadoDTO]: Lista de estados con id y nombre.
        """
        async with db.begin():
            estados = await self.estado_repository.list_estados(session=db)

        return [EstadoDTO(id=e.id, nombre=e.nombre) for e in estados]