# app/v1_0/repositories/banco_repository.py

from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1_0.models import Banco
from app.v1_0.entities import BancoDTO
from .base_repository import BaseRepository

class BancoRepository(BaseRepository[Banco]):
    def __init__(self):
        super().__init__(Banco)

    async def create_banco(
        self,
        dto: BancoDTO,
        session: AsyncSession
    ) -> Banco:
        """
        Crea un nuevo Banco a partir del DTO y hace flush para asignar su ID.
        """
        banco = Banco(**dto.model_dump())
        await self.add(banco, session)
        return banco

    async def get_by_nombre(
        self,
        nombre: str,
        session: AsyncSession
    ) -> Optional[Banco]:
        """
        Obtiene un Banco por su nombre, o None si no existe.
        """
        stmt = select(Banco).where(Banco.nombre == nombre)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

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
        if not banco or banco.saldo < monto:
            return None

        banco.saldo -= monto
        banco.fecha_actualizacion = datetime.now()
        await self.update(banco, session)
        return banco
