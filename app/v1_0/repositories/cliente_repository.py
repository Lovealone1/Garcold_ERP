from typing import Optional, List, Tuple
from sqlalchemy import select, func
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
        """Crea un nuevo Cliente a partir del DTO y hace flush para asignar su ID."""
        cliente = Cliente(**dto.model_dump())
        await self.add(cliente, session)
        return cliente

    async def get_by_id(
        self,
        cliente_id: int,
        session: AsyncSession
    ) -> Optional[Cliente]:
        """Obtiene un Cliente por su ID, o None si no existe."""
        return await super().get_by_id(cliente_id, session)

    async def update_cliente(
    self,
    cliente_id: int,
    dto: ClienteDTO,
    session: AsyncSession
    ) -> Optional[Cliente]:
        """Actualiza solo los campos permitidos de un Cliente existente según el DTO."""
        cliente = await self.get_by_id(cliente_id, session)
        if not cliente:
            return None

        allowed_fields = {"nombre", "cc_nit", "correo", "celular", "direccion", "ciudad"}

        for field, value in dto.model_dump(exclude_unset=True).items():
            if field in allowed_fields:
                setattr(cliente, field, value)

        await self.update(cliente, session)
        return cliente

    async def update_saldo(
        self,
        cliente_id: int,
        nuevo_saldo: float,
        session: AsyncSession
    ) -> Optional[Cliente]:
        """Actualiza únicamente el saldo de un Cliente."""
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
        """Elimina un Cliente dado su ID; retorna True si existía."""
        cliente = await self.get_by_id(cliente_id, session)
        if not cliente:
            return False

        await self.delete(cliente, session)
        return True

    async def list_clientes(
    self,
    session: AsyncSession
    ) -> List[Tuple[int, str]]:
        """
        Lista TODOS los clientes (sin paginación) devolviendo solo (id, nombre),
        ordenados alfabéticamente por nombre.
        """
        stmt = select(Cliente.id, Cliente.nombre).order_by(Cliente.nombre.asc())
        result = await session.execute(stmt)
        return [(cid, nombre) for cid, nombre in result.all()]

    async def list_paginated(
        self,
        offset: int,
        limit: int,
        session: AsyncSession
    ) -> Tuple[List[Cliente], int]:
        """Lista paginada con total."""
        stmt = (
            select(Cliente)
            .order_by(Cliente.id.asc())
            .offset(offset)
            .limit(limit)
        )
        items = (await session.execute(stmt)).scalars().all()
        total = await session.scalar(select(func.count(Cliente.id)))
        return items, int(total or 0)
