# app/v1_0/repositories/compra_repository.py

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any

from app.v1_0.models import Compra
from app.v1_0.entities import CompraDTO
from .base_repository import BaseRepository

class CompraRepository(BaseRepository[Compra]):
    def __init__(self):
        super().__init__(Compra)

    async def create_compra(
        self,
        dto: CompraDTO,
        session: AsyncSession
    ) -> Compra:
        """
        Crea una nueva Compra a partir de un DTO, añade al session y flush
        para asignar la PK sin hacer commit.
        """
        compra = Compra(**dto.model_dump())
        session.add(compra)
        await session.flush()
        return compra

    async def get_by_id(
        self,
        compra_id: int,
        session: AsyncSession
    ) -> Optional[Compra]:
        """
        Devuelve la Compra con el ID dado o None.
        """
        return await super().get_by_id(compra_id, session=session)

    async def get_by_proveedor(
        self,
        proveedor_id: int,
        session: AsyncSession
    ) -> List[Compra]:
        """
        Trae todas las Compras asociadas a un proveedor.
        """
        stmt = select(Compra).where(Compra.proveedor_id == proveedor_id)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def update_compra(
        self,
        compra_id: int,
        data: Dict[str, Any],
        session: AsyncSession
    ) -> Optional[Compra]:
        """
        Actualiza campos de una Compra existente, acepta un dict de {campo:valor}.
        No hace commit: deja flush/commit a la transacción externa.
        """
        compra = await session.get(Compra, compra_id)
        if not compra:
            return None

        for field, value in data.items():
            setattr(compra, field, value)

        # aplica cambios en la misma transacción
        await session.flush()
        await session.refresh(compra)
        return compra

    async def delete_compra(
        self,
        compra_id: int,
        session: AsyncSession
    ) -> bool:
        """
        Elimina la Compra con el ID dado y retorna True si existía.
        """
        compra = await self.get_by_id(compra_id, session)
        if not compra:
            return False

        await session.delete(compra)
        await session.flush()
        return True
