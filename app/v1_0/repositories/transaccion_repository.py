# app/v1_0/repositories/transaccion_repository.py

from typing import List
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1_0.models import Transaccion
from app.v1_0.entities import TransaccionDTO
from .base_repository import BaseRepository


class TransaccionRepository(BaseRepository[Transaccion]):
    """
    Repositorio para operaciones CRUD sobre la entidad Transaccion.
    Cada método recibe explícitamente una AsyncSession.
    """

    def __init__(self):
        super().__init__(Transaccion)

    async def create_transaccion(
        self,
        transaccion_dto: TransaccionDTO,
        session: AsyncSession
    ) -> Transaccion:
        """
        Crea una nueva Transaccion a partir del DTO y hace flush/commit
        para asignar su ID.

        Args:
            transaccion_dto (TransaccionDTO): DTO con los datos de la transacción.
            session (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            Transaccion: La entidad Transaccion recién creada.
        """
        transaccion = Transaccion(**transaccion_dto.model_dump())
        await self.add(transaccion, session)
        return transaccion

    async def list_transacciones(
        self,
        session: AsyncSession,
        limit: int = 10,
        offset: int = 0
    ) -> List[Transaccion]:
        """
        Recupera todas las transacciones paginadas.

        Args:
            session (AsyncSession): Sesión asíncrona de SQLAlchemy.
            limit (int): Número máximo de registros a devolver.
            offset (int): Número de registros a saltar.

        Returns:
            List[Transaccion]: Lista de transacciones.
        """
        stmt = (
            select(Transaccion)
            .order_by(desc(Transaccion.fecha))
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def list_by_tipo(
        self,
        tipo_id: int,
        session: AsyncSession,
        limit: int = 10,
        offset: int = 0
    ) -> List[Transaccion]:
        """
        Recupera transacciones de un tipo específico, paginadas.

        Args:
            tipo_id (int): ID del tipo de transacción.
            session (AsyncSession): Sesión asíncrona de SQLAlchemy.
            limit (int): Número máximo de registros a devolver.
            offset (int): Número de registros a saltar.

        Returns:
            List[Transaccion]: Lista de transacciones filtradas por tipo.
        """
        stmt = (
            select(Transaccion)
            .where(Transaccion.tipo_id == tipo_id)
            .order_by(desc(Transaccion.fecha))
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def delete_transaccion(
        self,
        transaccion_id: int,
        session: AsyncSession
    ) -> bool:
        """
        Elimina una transacción por su ID.

        Args:
            transaccion_id (int): ID de la transacción a eliminar.
            session (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            bool: True si existía y se borró, False en caso contrario.
        """
        transaccion = await self.get_by_id(transaccion_id, session)
        if not transaccion:
            return False
        await self.delete(transaccion, session)
        return True
