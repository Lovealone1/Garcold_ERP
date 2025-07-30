from typing import List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1_0.models import DetallePagoVenta
from app.v1_0.entities import DetallePagoVentaDTO
from .base_repository import BaseRepository

class DetallePagoVentaRepository(BaseRepository[DetallePagoVenta]):
    def __init__(self):
        super().__init__(DetallePagoVenta)

    async def create_pago(
        self,
        dto: DetallePagoVentaDTO,
        session: AsyncSession
    ) -> DetallePagoVenta:
        """
        Inserta un nuevo pago a una venta y devuelve la entidad persistida.
        """
        pago = DetallePagoVenta(**dto.model_dump())
        await self.add(pago, session)
        return pago

    async def list_by_venta(
        self,
        venta_id: int,
        session: AsyncSession
    ) -> List[DetallePagoVenta]:
        """
        Devuelve todos los pagos realizados sobre la venta indicada.
        """
        stmt = select(DetallePagoVenta).where(DetallePagoVenta.venta_id == venta_id)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def delete_pago(
        self,
        pago_id: int,
        session: AsyncSession
    ) -> bool:
        """
        Elimina un pago concreto por su ID. Retorna True si existía.
        """
        pago = await self.get_by_id(pago_id, session)
        if not pago:
            return False
        await self.delete(pago, session)
        return True

    async def delete_by_venta(
        self,
        venta_id: int,
        session: AsyncSession
    ) -> int:
        """
        Elimina todos los pagos asociados a una venta y retorna cuántos borró.
        """
        stmt = delete(DetallePagoVenta).where(DetallePagoVenta.venta_id == venta_id)
        result = await session.execute(stmt)
        await session.flush()
        return result.rowcount
