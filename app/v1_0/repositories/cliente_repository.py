# app/v1_0/repositories/cliente_repository.py

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1_0.models import Cliente
from app.v1_0.entities import ClienteDTO
from .base_repository import BaseRepository

class ClienteRepository(BaseRepository[Cliente]):
    def __init__(self):
        super().__init__(Cliente)

    async def create_cliente(
        self,
        dto: ClienteDTO,
        session: AsyncSession
    ) -> Cliente:
        """
        Crea un nuevo Cliente a partir del DTO y hace flush para asignar su ID.
        """
        cliente = Cliente(**dto.model_dump())
        await self.add(cliente, session)
        return cliente

    async def get_by_cc_nit(
        self,
        cc_nit: str,
        session: AsyncSession
    ) -> Optional[Cliente]:
        """
        Obtiene un Cliente por su CC/NIT, o None si no existe.
        """
        stmt = select(Cliente).where(Cliente.cc_nit == cc_nit)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_nombre(
        self,
        nombre: str,
        session: AsyncSession
    ) -> List[Cliente]:
        """
        Busca clientes cuyo nombre contenga la cadena (case‑insensitive).
        """
        stmt = select(Cliente).where(Cliente.nombre.ilike(f"%{nombre}%"))
        result = await session.execute(stmt)
        return result.scalars().all()

    async def update_cliente(
        self,
        cliente_id: int,
        dto: ClienteDTO,
        session: AsyncSession
    ) -> Optional[Cliente]:
        """
        Actualiza los campos de un Cliente existente según el DTO.
        """
        cliente = await self.get_by_id(cliente_id, session)
        if not cliente:
            return None

        for field, value in dto.model_dump(exclude_unset=True).items():
            setattr(cliente, field, value)

        await self.update(cliente, session)
        return cliente

    async def update_saldo(
        self,
        cliente_id: int,
        nuevo_saldo: float,
        session: AsyncSession
    ) -> Optional[Cliente]:
        """
        Actualiza únicamente el saldo de un Cliente.
        """
        cliente = await self.get_by_id(cliente_id, session)
        if not cliente:
            return None

        cliente.saldo = nuevo_saldo
        await self.update(cliente, session)
        return cliente

    async def delete_cliente(
        self,
        cliente_id: int,
        session: AsyncSession
    ) -> bool:
        """
        Elimina un Cliente dado su ID; retorna True si existía.
        """
        cliente = await self.get_by_id(cliente_id, session)
        if not cliente:
            return False

        await self.delete(cliente, session)
        return True
