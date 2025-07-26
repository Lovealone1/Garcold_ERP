from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Callable, Optional

from app.v1_0.models import Cliente
from app.v1_0.repositories import BaseRepository
from app.v1_0.entities import ClienteDTO


class ClienteRepository(BaseRepository[Cliente]):
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        super().__init__(session_factory, Cliente)

    async def create_cliente(self, cliente_dto: ClienteDTO, session: Optional[AsyncSession] = None) -> Cliente:
        cliente = Cliente(**cliente_dto.model_dump())
        return await self.create(cliente, session=session)

    async def get_by_cc_nit(self, cc_nit: str, session: Optional[AsyncSession] = None) -> Cliente | None:
        session = session or await self.get_session()
        result = await session.execute(
            select(Cliente).where(Cliente.cc_nit == str(cc_nit))
        )
        return result.scalar_one_or_none()

    async def get_by_nombre(self, nombre: str, session: Optional[AsyncSession] = None) -> list[Cliente]:
        session = session or await self.get_session()
        result = await session.execute(
            select(Cliente).where(Cliente.nombre.ilike(f"%{nombre}%"))
        )
        return result.scalars().all()

    async def update_cliente(self, cliente_id: int, cliente_dto: ClienteDTO, session: Optional[AsyncSession] = None) -> Cliente | None:
        session = session or await self.get_session()
        cliente = await session.get(Cliente, cliente_id)
        if cliente:
            for field, value in cliente_dto.model_dump(exclude_unset=True).items():
                setattr(cliente, field, value)
            await session.commit()
            await session.refresh(cliente)
            return cliente
        return None

    async def update_saldo(self, cliente_id: int, nuevo_saldo: float, session: Optional[AsyncSession] = None) -> Cliente | None:
        session = session or await self.get_session()
        cliente = await session.get(Cliente, cliente_id)
        if cliente:
            cliente.saldo = nuevo_saldo
            await session.commit()
            await session.refresh(cliente)
        return cliente

    async def delete_cliente(self, cliente_id: int, session: Optional[AsyncSession] = None) -> bool:
        session = session or await self.get_session()
        cliente = await session.get(Cliente, cliente_id)
        if cliente:
            await session.delete(cliente)
            await session.commit()
            return True
        return False
