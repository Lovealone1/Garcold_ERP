from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1_0.repositories.cliente_repository import ClienteRepository
from app.v1_0.entities import ClienteDTO
from app.v1_0.models import Cliente

PAGE_SIZE = 10

class ClienteService:
    def __init__(self, cliente_repository: ClienteRepository):
        self.cliente_repository = cliente_repository

    async def crear_cliente(
        self,
        cliente_dto: ClienteDTO,
        db: AsyncSession
    ) -> Cliente:
        async with db.begin():
            existente = await self.cliente_repository.get_by_cc_nit(
                cliente_dto.cc_nit,
                session=db
            )
            if existente:
                raise ValueError(f"Ya existe un cliente con NIT {cliente_dto.cc_nit}")
            if cliente_dto.celular and not cliente_dto.celular.isdigit():
                raise ValueError("El número de celular debe contener solo dígitos")
            cliente_dto.saldo = cliente_dto.saldo or 0.0
            return await self.cliente_repository.create_cliente(
                cliente_dto,
                session=db
            )

    async def actualizar_cliente(
        self,
        cliente_id: int,
        cliente_dto: ClienteDTO,
        db: AsyncSession
    ) -> Cliente:
        async with db.begin():
            cliente = await self.cliente_repository.get_by_id(
                cliente_id,
                session=db
            )
            if not cliente:
                raise ValueError("Cliente no encontrado")
            return await self.cliente_repository.update_cliente(
                cliente_id,
                cliente_dto,
                session=db
            )

    async def eliminar_cliente(
        self,
        cliente_id: int,
        db: AsyncSession
    ) -> bool:
        async with db.begin():
            cliente = await self.cliente_repository.get_by_id(
                cliente_id,
                session=db
            )
            if not cliente:
                raise ValueError("Cliente no encontrado")
            return await self.cliente_repository.delete_cliente(
                cliente_id,
                session=db
            )

    async def obtener_por_cc_nit(
        self,
        cc_nit: str,
        session: AsyncSession
    ) -> Optional[Cliente]:
        return await self.cliente_repository.get_by_cc_nit(
            cc_nit,
            session=session
        )

    async def obtener_por_nombre(
        self,
        nombre: str,
        db: AsyncSession
    ) -> List[Cliente]:
        async with db.begin():
            return await self.cliente_repository.get_by_nombre(
                nombre,
                session=db
            )

    async def listar_clientes(
        self,
        page: int,
        db: AsyncSession
    ) -> List[Cliente]:
        """
        Lista todos los clientes, 10 por página.
        """
        offset = (page - 1) * PAGE_SIZE
        async with db.begin():
            return await self.cliente_repository.list_paginated(
                offset,
                PAGE_SIZE,
                session=db
            )
