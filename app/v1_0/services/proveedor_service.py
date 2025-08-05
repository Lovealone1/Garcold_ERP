from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1_0.repositories.proveedor_repository import ProveedorRepository
from app.v1_0.entities import ProveedorDTO
from app.v1_0.models import Proveedor

PAGE_SIZE = 10

class ProveedorService:
    def __init__(self, proveedor_repository: ProveedorRepository):
        self.repository = proveedor_repository

    async def crear_proveedor(
        self,
        dto: ProveedorDTO,
        db: AsyncSession
    ) -> Proveedor:
        async with db.begin():
            existente = await self.repository.get_by_cc_nit(dto.cc_nit, session=db)
            if existente:
                raise ValueError(f"Ya existe un proveedor con NIT {dto.cc_nit}")
            return await self.repository.create_proveedor(dto, session=db)

    async def actualizar_proveedor(
        self,
        proveedor_id: int,
        dto: ProveedorDTO,
        db: AsyncSession
    ) -> Proveedor:
        async with db.begin():
            prov = await self.repository.get_by_id(proveedor_id, session=db)
            if not prov:
                raise ValueError("Proveedor no encontrado")
            return await self.repository.update_proveedor(proveedor_id, dto, session=db)

    async def eliminar_proveedor(
        self,
        proveedor_id: int,
        db: AsyncSession
    ) -> bool:
        async with db.begin():
            prov = await self.repository.get_by_id(proveedor_id, session=db)
            if not prov:
                raise ValueError("Proveedor no encontrado")
            return await self.repository.delete_proveedor(proveedor_id, session=db)

    async def obtener_por_cc_nit(
        self,
        cc_nit: str,
        session: AsyncSession
    ) -> Optional[Proveedor]:
        return await self.repository.get_by_cc_nit(cc_nit, session=session)

    async def obtener_por_nombre(
        self,
        nombre: str,
        session: AsyncSession
    ) -> List[Proveedor]:
        return await self.repository.get_by_nombre(nombre, session=session)

    async def listar_proveedores(
        self,
        page: int,
        db: AsyncSession
    ) -> List[Proveedor]:
        offset = (page - 1) * PAGE_SIZE
        async with db.begin():
            return await self.repository.list_paginated(offset, PAGE_SIZE, session=db)