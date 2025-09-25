from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from math import ceil

from app.v1_0.repositories.cliente_repository import ClienteRepository
from app.v1_0.entities import ClienteDTO, ClientesPageDTO, ClienteListDTO, ListClienteDTO
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
        """
        Crea cliente. Validaciones básicas; la unicidad por cc_nit
        debe estar en la capa de DB si aplica.
        """
        if cliente_dto.celular and not cliente_dto.celular.isdigit():
            raise ValueError("El número de celular debe contener solo dígitos")

        # Normalizar valores
        cliente_dto.saldo = cliente_dto.saldo or 0.0
        if cliente_dto.ciudad:
            cliente_dto.ciudad = cliente_dto.ciudad.upper().strip()

        async with db.begin():
            return await self.cliente_repository.create_cliente(cliente_dto, session=db)

    async def obtener_por_id(
        self,
        cliente_id: int,
        db: AsyncSession
    ) -> Optional[Cliente]:
        """Retorna el cliente por ID o None."""
        async with db.begin():
            return await self.cliente_repository.get_by_id(cliente_id, session=db)

    async def actualizar_cliente(
        self,
        cliente_id: int,
        cliente_dto: ClienteDTO,
        db: AsyncSession
    ) -> Cliente:
        """Actualiza datos del cliente."""
        async with db.begin():
            cliente = await self.cliente_repository.get_by_id(cliente_id, session=db)
            if not cliente:
                raise ValueError("Cliente no encontrado")
            return await self.cliente_repository.update_cliente(cliente_id, cliente_dto, session=db)

    async def actualizar_saldo(
        self,
        cliente_id: int,
        nuevo_saldo: float,
        db: AsyncSession
    ) -> Cliente:
        """Actualiza sólo el saldo del cliente."""
        async with db.begin():
            cliente = await self.cliente_repository.update_saldo(cliente_id, nuevo_saldo, session=db)
            if not cliente:
                raise ValueError("Cliente no encontrado")
            return cliente

    async def eliminar_cliente(
        self,
        cliente_id: int,
        db: AsyncSession
    ) -> bool:
        """Elimina cliente por ID."""
        async with db.begin():
            cliente = await self.cliente_repository.get_by_id(cliente_id, session=db)
            if not cliente:
                raise ValueError("Cliente no encontrado")
            return await self.cliente_repository.delete_cliente(cliente_id, session=db)

    async def listar_clientes(self, page: int, db: AsyncSession) -> ClientesPageDTO:
        """Lista clientes paginados con metadatos."""
        offset = (page - 1) * PAGE_SIZE
        async with db.begin():
            items, total = await self.cliente_repository.list_paginated(
                offset=offset, limit=PAGE_SIZE, session=db
            )

        total = int(total or 0)
        total_pages = max(1, ceil(total / PAGE_SIZE)) if total else 1

        return ClientesPageDTO(
            items=[
                ClienteListDTO(
                    id=c.id,
                    nombre=c.nombre,
                    cc_nit=c.cc_nit,
                    correo=c.correo,
                    direccion=c.direccion,
                    celular=c.celular,
                    ciudad=c.ciudad,
                    saldo=c.saldo,
                    fecha_creacion=c.fecha_creacion
                )
                for c in items
            ],
            page=page,
            page_size=PAGE_SIZE,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )

    async def listar_clientes_all(
        self,
        db: AsyncSession,
    ) -> List[ListClienteDTO]:
        """
        Lista TODOS los clientes (sin paginación) devolviendo ClienteListDTO
        con solo id y nombre (resto de campos quedan por defecto).
        """
        async with db.begin():
            rows = await self.cliente_repository.list_clientes(session=db)

        return [ListClienteDTO(id=cid, nombre=nombre) for cid, nombre in rows]