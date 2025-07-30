from typing import Optional, List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1_0.models import DetallePagoCompra
from app.v1_0.entities import DetallePagoCompraDTO
from .base_repository import BaseRepository

class DetallePagoCompraRepository(BaseRepository[DetallePagoCompra]):
    def __init__(self):
        super().__init__(DetallePagoCompra)

    async def create_pago(
        self,
        dto: DetallePagoCompraDTO,
        session: AsyncSession
    ) -> DetallePagoCompra:
        """
        Inserta un nuevo pago a una compra y devuelve la entidad persistida.
        """
        pago = DetallePagoCompra(**dto.model_dump())
        await self.add(pago, session)
        return pago

    async def list_by_compra(
        self,
        compra_id: int,
        session: AsyncSession
    ) -> List[DetallePagoCompra]:
        """
        Devuelve todos los pagos realizados sobre la compra indicada.
        """
        stmt = select(DetallePagoCompra).where(DetallePagoCompra.compra_id == compra_id)
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

    async def delete_by_compra(
        self,
        compra_id: int,
        session: AsyncSession
    ) -> int:
        """
        Elimina todos los pagos asociados a una compra y retorna cuántos borró.
        """
        stmt = delete(DetallePagoCompra).where(DetallePagoCompra.compra_id == compra_id)
        result = await session.execute(stmt)
        await session.flush()
        return result.rowcount
