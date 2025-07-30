# app/v1_0/repositories/credito_repository.py

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1_0.models import Credito
from app.v1_0.entities import CreditoDTO
from .base_repository import BaseRepository


class CreditoRepository(BaseRepository[Credito]):
    """
    Repositorio para CRUD de la entidad Credito.
    Cada método recibe explícitamente una AsyncSession.
    """

    def __init__(self):
        super().__init__(Credito)

    async def create_credito(
        self,
        credito_dto: CreditoDTO,
        session: AsyncSession
    ) -> Credito:
        """
        Crea un nuevo registro de Credito a partir del DTO,
        hace commit y refresh para asignar su ID.

        Args:
            credito_dto (CreditoDTO): DTO con los datos del crédito.
            session (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            Credito: La entidad Credito recién creada.
        """
        credito = Credito(**credito_dto.model_dump())
        await self.add(credito, session)
        return credito

    async def get_by_nombre(
        self,
        nombre: str,
        session: AsyncSession
    ) -> List[Credito]:
        """
        Recupera todos los Créditos cuyo nombre contenga la cadena dada
        (case‑insensitive).

        Args:
            nombre (str): Subcadena a buscar en el nombre.
            session (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            List[Credito]: Créditos que coinciden con el filtro.
        """
        stmt = select(Credito).where(Credito.nombre.ilike(f"%{nombre}%"))
        result = await session.execute(stmt)
        return result.scalars().all()

    async def update_monto(
        self,
        credito_id: int,
        nuevo_monto: float,
        session: AsyncSession
    ) -> Optional[Credito]:
        """
        Actualiza el monto de un Credito existente y hace commit/refresh.

        Args:
            credito_id (int): ID del crédito a actualizar.
            nuevo_monto (float): Nuevo valor para el campo monto.
            session (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            Optional[Credito]: La entidad actualizada, o None si no existe.
        """
        credito = await self.get_by_id(credito_id, session)
        if not credito:
            return None

        credito.monto = nuevo_monto
        await session.commit()
        await session.refresh(credito)
        return credito

    async def delete_credito(
        self,
        credito_id: int,
        session: AsyncSession
    ) -> bool:
        """
        Elimina un Credito dado su ID; retorna True si existía y fue borrado.

        Args:
            credito_id (int): ID del crédito a eliminar.
            session (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            bool: True si existía y se eliminó, False en caso contrario.
        """
        credito = await self.get_by_id(credito_id, session)
        if not credito:
            return False
        await self.delete(credito, session)
        return True
