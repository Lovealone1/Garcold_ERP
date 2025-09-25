from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from math import ceil

from app.v1_0.repositories.proveedor_repository import ProveedorRepository
from app.v1_0.entities import ProveedorDTO, ProveedoresPageDTO, ProveedorListDTO
from app.v1_0.models import Proveedor

PAGE_SIZE = 10


class ProveedorService:
    def __init__(self, proveedor_repository: ProveedorRepository):
        self.proveedor_repository = proveedor_repository

    async def crear_proveedor(
        self,
        proveedor_dto: ProveedorDTO,
        db: AsyncSession
    ) -> Proveedor:
        """
        Crea proveedor. Valida celular numérico y normaliza ciudad.
        La unicidad por cc_nit debe resolverse en DB si aplica.
        """
        if proveedor_dto.celular and not proveedor_dto.celular.isdigit():
            raise ValueError("El número de celular debe contener solo dígitos")

        if proveedor_dto.ciudad:
            proveedor_dto.ciudad = proveedor_dto.ciudad.upper().strip()

        async with db.begin():
            return await self.proveedor_repository.create_proveedor(proveedor_dto, session=db)

    async def obtener_por_id(
        self,
        proveedor_id: int,
        db: AsyncSession
    ) -> Optional[Proveedor]:
        """Retorna el proveedor por ID o None."""
        async with db.begin():
            return await self.proveedor_repository.get_by_id(proveedor_id, session=db)

    async def actualizar_proveedor(
        self,
        proveedor_id: int,
        proveedor_dto: ProveedorDTO,
        db: AsyncSession
    ) -> Proveedor:
        """Actualiza datos del proveedor."""
        async with db.begin():
            prov = await self.proveedor_repository.get_by_id(proveedor_id, session=db)
            if not prov:
                raise ValueError("Proveedor no encontrado")
            return await self.proveedor_repository.update_proveedor(proveedor_id, proveedor_dto, session=db)

    async def eliminar_proveedor(
        self,
        proveedor_id: int,
        db: AsyncSession
    ) -> bool:
        """Elimina proveedor por ID."""
        async with db.begin():
            prov = await self.proveedor_repository.get_by_id(proveedor_id, session=db)
            if not prov:
                raise ValueError("Proveedor no encontrado")
            return await self.proveedor_repository.delete_proveedor(proveedor_id, session=db)

    async def listar_proveedores(
        self,
        page: int,
        db: AsyncSession
    ) -> ProveedoresPageDTO:
        """Lista proveedores paginados con metadatos."""
        offset = (page - 1) * PAGE_SIZE
        async with db.begin():
            items, total = await self.proveedor_repository.list_paginated(
                offset=offset, limit=PAGE_SIZE, session=db
            )

        total = int(total or 0)
        total_pages = max(1, ceil(total / PAGE_SIZE)) if total else 1

        return ProveedoresPageDTO(
            items=[
                ProveedorListDTO(
                    id=p.id,
                    nombre=p.nombre,
                    cc_nit=p.cc_nit,
                    correo=p.correo,
                    celular=p.celular,
                    direccion=p.direccion,
                    ciudad=p.ciudad,
                    fecha_creacion=p.fecha_creacion,
                )
                for p in items
            ],
            page=page,
            page_size=PAGE_SIZE,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )
