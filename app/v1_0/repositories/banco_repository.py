# app/v1_0/repositories/banco_repository.py

from datetime import datetime
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1_0.models import Banco
from app.v1_0.schemas.banco_schema import BancoCreateSchema
from .base_repository import BaseRepository

class BancoRepository(BaseRepository[Banco]):
    def __init__(self):
        super().__init__(Banco)

    async def create_banco(
        self,
        dto: BancoCreateSchema,
        session: AsyncSession
    ) -> Banco:
        """
        Crea un nuevo Banco a partir del DTO y hace flush para asignar su ID.
        """
        banco = Banco(**dto.model_dump())
        await self.add(banco, session)
        return banco

    async def update_saldo(
        self,
        banco_id: int,
        nuevo_saldo: float,
        session: AsyncSession
    ) -> Optional[Banco]:
        """
        Establece el saldo de un Banco y actualiza la fecha.
        """
        banco = await self.get_by_id(banco_id, session)
        if not banco:
            return None

        banco.saldo = nuevo_saldo
        banco.fecha_actualizacion = datetime.now()
        await self.update(banco, session)
        return banco

    async def delete_banco(
        self,
        banco_id: int,
        session: AsyncSession
    ) -> bool:
        """
        Elimina un Banco dado su ID.

        Parameters
        ----------
        banco_id : int
            ID del banco a eliminar.
        session : AsyncSession
            Sesión async de SQLAlchemy.

        Returns
        -------
        bool
            True si el banco existía y fue eliminado, False si no existe.
        """
        banco = await self.get_by_id(banco_id, session)
        if not banco:
            return False

        await self.delete(banco, session)
        return True

    async def aumentar_saldo(
        self,
        banco_id: int,
        monto: float,
        session: AsyncSession
    ) -> Optional[Banco]:
        """
        Incrementa el saldo de un Banco y actualiza la fecha.
        """
        banco = await self.get_by_id(banco_id, session)
        if not banco:
            return None

        banco.saldo += monto
        banco.fecha_actualizacion = datetime.now()
        await self.update(banco, session)
        return banco

    async def disminuir_saldo(
        self,
        banco_id: int,
        monto: float,
        session: AsyncSession
    ) -> Optional[Banco]:
        """
        Decrementa el saldo de un Banco (si hay suficiente saldo) y actualiza la fecha.
        """
        banco = await self.get_by_id(banco_id, session)
        if not banco:
            return None

        banco.saldo -= monto
        banco.fecha_actualizacion = datetime.now()
        await self.update(banco, session)
        return banco

    async def list_bancos(
            self,
            session: AsyncSession
        ) -> List[Banco]:
            """
            Retorna todos los Bancos con todos sus campos.

            Parameters
            ----------
            session : AsyncSession
                Sesión async de SQLAlchemy.

            Returns
            -------
            List[Banco]
                Lista de instancias de modelo Banco.
            """
            result = await session.execute(select(Banco))
            return list(result.scalars().all())