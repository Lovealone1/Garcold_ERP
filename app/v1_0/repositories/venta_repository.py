from typing import Optional, List, Union, Dict, Any, Tuple
from sqlalchemy import select, func
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
        data: Union[VentaDTO, Dict[str, Any]],
        session: AsyncSession
    ) -> Optional[Venta]:
        """
        Actualiza los campos de una Venta existente. Acepta un DTO o un dict
        con los nombres de campo y valores a modificar. No hace commit; deja
        el flush/commit a la transacción externa.

        Args:
            venta_id: ID de la venta a actualizar.
            data:     VentaDTO o dict con los campos a cambiar.
            session:  Sesión asíncrona de SQLAlchemy.

        Returns:
            La entidad Venta actualizada, o None si no existe.
        """

        venta = await session.get(Venta, venta_id)
        if not venta:
            return None

        if isinstance(data, dict):
            updates = data
        else:
            updates = data.model_dump(exclude_unset=True)

        for field, value in updates.items():
            setattr(venta, field, value)

        await session.flush()
        await session.refresh(venta)
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

    async def list_paginated(
        self,
        offset: int,
        limit: int,
        session: AsyncSession
    ) -> Tuple[List[Venta], int]:
        """
        Lista ventas paginadas, ordenadas por ID ascendente.
        Retorna (items, total).
        """
        stmt = (
            select(Venta)
            .order_by(Venta.id.asc())
            .offset(offset)
            .limit(limit)
        )
        items = (await session.execute(stmt)).scalars().all()
        total = await session.scalar(select(func.count(Venta.id)))
        return items, int(total or 0)