from typing import Optional, List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1_0.schemas.venta_schema import DetalleVentaCreate
from app.v1_0.models import DetalleVenta
from app.v1_0.entities import DetalleVentaDTO
from .base_repository import BaseRepository

class DetalleVentaRepository(BaseRepository[DetalleVenta]):
    def __init__(self):
        super().__init__(DetalleVenta)

    async def create_detalle(
        self,
        dto: DetalleVentaDTO,
        session: AsyncSession
    ) -> DetalleVenta:
        """
        Crea un DetalleVenta a partir del DTO y hace flush para asignar su ID.
        """
        detalle = DetalleVenta(**dto.model_dump())
        await self.add(detalle, session)
        return detalle

    async def get_by_venta_id(
        self,
        venta_id: int,
        session: AsyncSession
    ) -> List[DetalleVenta]:
        """
        Recupera todos los DetalleVenta asociados a una venta.
        """
        stmt = select(DetalleVenta).where(DetalleVenta.venta_id == venta_id)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def delete_detalle(
        self,
        detalle_id: int,
        session: AsyncSession
    ) -> bool:
        """
        Elimina un DetalleVenta dado su ID.
        """
        detalle = await self.get_by_id(detalle_id, session)
        if not detalle:
            return False

        await self.delete(detalle, session)
        return True

    async def bulk_insert_detalles(
    self,
    dtos: list[DetalleVentaCreate],
    session: AsyncSession,
    ) -> list[DetalleVenta]:
        objects = [
            DetalleVenta(
                venta_id=d.venta_id,
                producto_id=d.producto_id,
                cantidad=d.cantidad,
                precio_producto=d.precio_producto,
            )
            for d in dtos
        ]
        session.add_all(objects)
        await session.flush()
        return objects
    
    async def delete_by_venta(
        self,
        venta_id: int,
        session: AsyncSession
    ) -> int:
        """
        Elimina todos los DetalleVenta asociados a la venta_id dada
        y retorna el número de filas eliminadas.
        """
        stmt = delete(DetalleVenta).where(DetalleVenta.venta_id == venta_id)
        result = await session.execute(stmt)
        await session.flush()
        return result.rowcount