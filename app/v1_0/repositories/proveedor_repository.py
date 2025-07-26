# app/v1_0/repositories/proveedor_repository.py

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1_0.models import Proveedor
from app.v1_0.entities import ProveedorDTO
from .base_repository import BaseRepository

class ProveedorRepository(BaseRepository[Proveedor]):
    def __init__(self):
        super().__init__(Proveedor)

    async def create_proveedor(
        self,
        dto: ProveedorDTO,
        session: AsyncSession
    ) -> Proveedor:
        """
        Crea un nuevo Proveedor a partir del DTO y hace flush para asignar su ID.
        """
        proveedor = Proveedor(**dto.model_dump())
        await self.add(proveedor, session)
        return proveedor

    async def get_by_cc_nit(
        self,
        cc_nit: str,
        session: AsyncSession
    ) -> Optional[Proveedor]:
        """
        Obtiene un Proveedor por su CC/NIT, o None si no existe.
        """
        stmt = select(Proveedor).where(Proveedor.cc_nit == cc_nit)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_nombre(
        self,
        nombre: str,
        session: AsyncSession
    ) -> List[Proveedor]:
        """
        Busca proveedores cuyo nombre contenga la cadena (case‑insensitive).
        """
        stmt = select(Proveedor).where(Proveedor.nombre.ilike(f"%{nombre}%"))
        result = await session.execute(stmt)
        return result.scalars().all()

    async def update_proveedor(
        self,
        proveedor_id: int,
        dto: ProveedorDTO,
        session: AsyncSession
    ) -> Optional[Proveedor]:
        """
        Actualiza un Proveedor existente con los campos proporcionados en el DTO.
        """
        proveedor = await self.get_by_id(proveedor_id, session)
        if not proveedor:
            return None

        for field, value in dto.model_dump(exclude_unset=True).items():
            setattr(proveedor, field, value)

        await self.update(proveedor, session)
        return proveedor

    async def delete_proveedor(
        self,
        proveedor_id: int,
        session: AsyncSession
    ) -> bool:
        """
        Elimina un Proveedor dado su ID.
        """
        proveedor = await self.get_by_id(proveedor_id, session)
        if not proveedor:
            return False

        await self.delete(proveedor, session)
        return True
