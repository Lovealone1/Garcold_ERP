# app/v1_0/repositories/inversion_repository.py

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1_0.models import Inversion
from app.v1_0.entities import InversionDTO
from .base_repository import BaseRepository


class InversionRepository(BaseRepository[Inversion]):
    """
    Repositorio para CRUD de inversiones.
    Cada método recibe explícitamente una AsyncSession.
    """

    def __init__(self):
        super().__init__(Inversion)

    async def create_inversion(
        self,
        inversion_dto: InversionDTO,
        session: AsyncSession
    ) -> Inversion:
        """
        Crea una nueva Inversion a partir del DTO,
        hace commit y refresh para asignar su ID.

        Args:
            inversion_dto (InversionDTO): DTO con los datos de la inversión.
            session (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            Inversion: La entidad recién creada.
        """
        inversion = Inversion(**inversion_dto.model_dump())
        await self.add(inversion, session)
        return inversion

    async def get_by_nombre(
        self,
        nombre: str,
        session: AsyncSession
    ) -> List[Inversion]:
        """
        Recupera todas las inversiones cuyo nombre contenga la cadena dada
        (case-insensitive).

        Args:
            nombre (str): Subcadena a buscar en el campo nombre.
            session (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            List[Inversion]: Lista de inversiones que coinciden.
        """
        stmt = select(Inversion).where(Inversion.nombre.ilike(f"%{nombre}%"))
        result = await session.execute(stmt)
        return result.scalars().all()

    async def update_saldo(
        self,
        inversion_id: int,
        nuevo_saldo: float,
        session: AsyncSession
    ) -> Optional[Inversion]:
        """
        Actualiza el saldo de una inversión existente,
        hace commit y refresh para reflejar el cambio.

        Args:
            inversion_id (int): ID de la inversión a actualizar.
            nuevo_saldo (float): Nuevo valor para el campo saldo.
            session (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            Optional[Inversion]: La entidad actualizada, o None si no existe.
        """
        inversion = await self.get_by_id(inversion_id, session)
        if not inversion:
            return None

        inversion.saldo = nuevo_saldo
        await session.commit()
        await session.refresh(inversion)
        return inversion

    async def delete_inversion(
        self,
        inversion_id: int,
        session: AsyncSession
    ) -> bool:
        """
        Elimina una inversión por su ID; retorna True si existía y fue borrada.

        Args:
            inversion_id (int): ID de la inversión a eliminar.
            session (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            bool: True si existía y se eliminó, False en caso contrario.
        """
        inversion = await self.get_by_id(inversion_id, session)
        if not inversion:
            return False

        await self.delete(inversion, session)
        return True
