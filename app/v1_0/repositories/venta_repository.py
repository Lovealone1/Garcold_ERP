from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1_0.models import Venta
from app.v1_0.entities import VentaDTO
from .base_repository import BaseRepository

class VentaRepository(BaseRepository[Venta]):
    def __init__(self):
        super().__init__(Venta)

    async def create_venta(
        self,
        dto: VentaDTO,
        session: AsyncSession
    ) -> Venta:
        """
        Crea una nueva Venta a partir del DTO y hace flush para asignar su ID.
        """
        venta = Venta(**dto.model_dump())
        await self.add(venta, session)
        return venta

    async def get_by_id(
        self,
        venta_id: int,
        session: AsyncSession
    ) -> Optional[Venta]:
        """
        Recupera una Venta por su ID.
        """
        return await super().get_by_id(venta_id, session)

    async def get_all(
        self,
        session: AsyncSession
    ) -> List[Venta]:
        """
        Recupera todas las Ventas.
        """
        return await super().get_all(session)

    async def update_venta(
        self,
        venta_id: int,
        dto: VentaDTO,
        session: AsyncSession
    ) -> Optional[Venta]:
        """
        Actualiza los campos de una Venta existente según el DTO.
        """
        venta = await self.get_by_id(venta_id, session)
        if not venta:
            return None

        for field, value in dto.model_dump(exclude_unset=True).items():
            setattr(venta, field, value)

        await self.update(venta, session)
        return venta

    async def delete_venta(
        self,
        venta_id: int,
        session: AsyncSession
    ) -> bool:
        """
        Elimina la Venta con el ID dado y retorna True si existía.
        """
        venta = await self.get_by_id(venta_id, session)
        if not venta:
            return False

        await self.delete(venta, session)
        return True
