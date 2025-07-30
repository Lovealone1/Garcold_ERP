from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import date

from app.v1_0.models import Gasto
from app.v1_0.repositories import BaseRepository
from app.v1_0.entities import GastoDTO  


class GastoRepository(BaseRepository[Gasto]):
    """
    Repositorio para CRUD de gastos. Cada método recibe explícitamente
    una AsyncSession, al igual que los demás repositorios.
    """

    def __init__(self):
        super().__init__(Gasto)

    async def create_gasto(
        self,
        gasto_dto: GastoDTO,
        session: AsyncSession
    ) -> Gasto:
        """
        Crea un gasto a partir del DTO y hace flush/commit para asignar su ID.

        Args:
            gasto_dto (GastoDTO): DTO con los datos del gasto.
            session (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            Gasto: La entidad recién creada.
        """
        gasto = Gasto(**gasto_dto.model_dump())
        await self.add(gasto, session)
        return gasto

    async def get_by_fecha(
        self,
        fecha: date,
        session: AsyncSession
    ) -> List[Gasto]:
        """
        Recupera todos los gastos cuya fecha coincida con `fecha`.

        Args:
            fecha (date): Fecha de los gastos a buscar.
            session (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            List[Gasto]: Lista de gastos encontrados.
        """
        stmt = select(Gasto).where(Gasto.fecha_gasto == fecha)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_by_categoria(
        self,
        categoria_id: int,
        session: AsyncSession
    ) -> List[Gasto]:
        """
        Recupera todos los gastos de una categoría específica.

        Args:
            categoria_id (int): ID de la categoría de gasto.
            session (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            List[Gasto]: Lista de gastos encontrados.
        """
        stmt = select(Gasto).where(Gasto.categoria_gasto_id == categoria_id)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def delete_gasto(
        self,
        gasto_id: int,
        session: AsyncSession
    ) -> bool:
        """
        Elimina un gasto por su ID; retorna True si existía y fue borrado.

        Args:
            gasto_id (int): ID del gasto a eliminar.
            session (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            bool: True si el gasto existía y se eliminó, False en caso contrario.
        """
        gasto = await self.get_by_id(gasto_id, session)
        if not gasto:
            return False
        await self.delete(gasto, session)
        return True
