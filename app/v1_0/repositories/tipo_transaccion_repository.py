from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1_0.models import TipoTransaccion
from app.v1_0.repositories.base_repository import BaseRepository


class TipoTransaccionRepository(BaseRepository[TipoTransaccion]):
    """
    Repositorio para CRUD de la entidad TipoTransaccion.
    Cada método recibe explícitamente una AsyncSession.
    """

    def __init__(self):
        super().__init__(TipoTransaccion)

    async def create_tipo(
        self,
        nombre: str,
        session: AsyncSession
    ) -> TipoTransaccion:
        """
        Crea un nuevo TipoTransaccion con el nombre indicado.

        Args:
            nombre (str): Nombre del nuevo tipo de transacción.
            session (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            TipoTransaccion: La entidad recién creada.
        """
        tipo = TipoTransaccion(nombre=nombre)
        await self.add(tipo, session)
        return tipo

    async def get_by_id(
        self,
        tipo_id: int,
        session: AsyncSession
    ) -> Optional[TipoTransaccion]:
        """
        Recupera un TipoTransaccion por su ID.

        Args:
            tipo_id (int): ID del tipo de transacción.
            session (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            Optional[TipoTransaccion]: La entidad encontrada o None.
        """
        return await super().get_by_id(tipo_id, session)

    async def get_by_nombre(
        self,
        nombre: str,
        session: AsyncSession
    ) -> Optional[TipoTransaccion]:
        """
        Recupera un TipoTransaccion que coincida exactamente con el nombre dado (case-insensitive).

        Args:
            nombre (str): Nombre exacto (o parcial) a buscar.
            session (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            Optional[TipoTransaccion]: La entidad encontrada o None.
        """
        stmt = select(TipoTransaccion).where(TipoTransaccion.nombre.ilike(nombre))
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        session: AsyncSession
    ) -> List[TipoTransaccion]:
        """
        Recupera todos los tipos de transacción.

        Args:
            session (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            List[TipoTransaccion]: Lista de todos los tipos.
        """
        return await super().get_all(session)