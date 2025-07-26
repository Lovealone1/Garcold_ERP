from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import Callable, Optional

from app.v1_0.models import Banco
from app.v1_0.entities import BancoDTO
from app.v1_0.repositories import BaseRepository


class BancoRepository(BaseRepository[Banco]):
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        super().__init__(session_factory, Banco)

    async def create_banco(self, banco_dto: BancoDTO, session: Optional[AsyncSession] = None) -> Banco:
        banco = Banco(**banco_dto.model_dump())
        return await self.create(banco, session=session)

    async def get_by_nombre(self, nombre: str, session: Optional[AsyncSession] = None) -> Banco | None:
        session = session or await self.get_session()
        result = await session.execute(
            select(Banco).where(Banco.nombre == nombre)
        )
        return result.scalar_one_or_none()

    async def update_saldo(self, banco_id: int, nuevo_saldo: float, session: Optional[AsyncSession] = None) -> Banco | None:
        session = session or await self.get_session()
        banco = await session.get(Banco, banco_id)
        if banco:
            banco.saldo = nuevo_saldo
            banco.fecha_actualizacion = datetime.now()
            await session.commit()
            await session.refresh(banco)
            return banco
        return None

    async def _aumentar_saldo(self, banco_id: int, monto: float, session: Optional[AsyncSession] = None) -> Banco | None:
        session = session or await self.get_session()
        banco = await session.get(Banco, banco_id)
        if banco:
            banco.saldo += monto
            banco.fecha_actualizacion = datetime.now()
            await session.commit()
            await session.refresh(banco)
            return banco
        return None

    async def _disminuir_saldo(self, banco_id: int, monto: float, session: Optional[AsyncSession] = None) -> Banco | None:
        session = session or await self.get_session()
        banco = await session.get(Banco, banco_id)
        if banco and banco.saldo >= monto:
            banco.saldo -= monto
            banco.fecha_actualizacion = datetime.now()
            await session.commit()
            await session.refresh(banco)
            return banco
        return None
