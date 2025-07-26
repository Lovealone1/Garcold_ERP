# app/v1_0/repositories/detalle_compra_repository.py

from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1_0.models import DetalleCompra
from app.v1_0.entities import DetalleCompraDTO
from .base_repository import BaseRepository

class DetalleCompraRepository(BaseRepository[DetalleCompra]):
    def __init__(self):
        super().__init__(DetalleCompra)

    async def create_detalle(
        self,
        dto: DetalleCompraDTO,
        session: AsyncSession
    ) -> DetalleCompra:
        """
        Crea un DetalleCompra a partir del DTO, lo añade al session y hace flush.
        """
        detalle = DetalleCompra(**dto.model_dump())
        await self.add(detalle, session)
        return detalle

    async def get_by_compra_id(
        self,
        compra_id: int,
        session: AsyncSession
    ) -> List[DetalleCompra]:
        """
        Recupera todos los detalles asociados a una compra.
        """
        stmt = select(DetalleCompra).where(DetalleCompra.compra_id == compra_id)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def update_detalle(
        self,
        detalle_id: int,
        dto: DetalleCompraDTO,
        session: AsyncSession
    ) -> Optional[DetalleCompra]:
        """
        Actualiza un DetalleCompra existente con los campos proporcionados en el DTO.
        """
        detalle = await self.get_by_id(detalle_id, session)
        if not detalle:
            return None

        for field, value in dto.model_dump(exclude_unset=True).items():
            setattr(detalle, field, value)

        await self.update(detalle, session)
        return detalle

    async def delete_detalle(
        self,
        detalle_id: int,
        session: AsyncSession
    ) -> bool:
        """
        Elimina un DetalleCompra dado su ID.
        """
        detalle = await self.get_by_id(detalle_id, session)
        if not detalle:
            return False

        await self.delete(detalle, session)
        return True

    async def bulk_insert_detalles(
        self,
        dtos: List[DetalleCompraDTO],
        session: AsyncSession
    ) -> List[DetalleCompra]:
        """
        Inserta en lote múltiples DetalleCompra a partir de una lista de DTOs.
        """
        objects = [DetalleCompra(**dto.model_dump(exclude={"total"})) for dto in dtos]
        session.add_all(objects)
        await session.flush()
        return objects
    
    async def delete_by_compra(
            self,
            compra_id: int,
            session: AsyncSession
        ) -> int:
            """
            Elimina todos los DetalleCompra asociados a la compra_id dada
            y retorna el número de filas eliminadas.
            """
            stmt = delete(DetalleCompra).where(DetalleCompra.compra_id == compra_id)
            result = await session.execute(stmt)
            await session.flush()
            return result.rowcount