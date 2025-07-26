from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Callable, Optional

from app.v1_0.models import Compra
from app.v1_0.repositories import BaseRepository
from app.v1_0.entities import CompraDTO

class CompraRepository(BaseRepository):
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        super().__init__(session_factory, Compra)

    async def create_compra(self, compra_dto: CompraDTO, session: Optional[AsyncSession] = None) -> Compra:
        compra = Compra(**compra_dto.model_dump())
        return await self.create(compra, session=session)

    async def get_by_id(self, compra_id: int, session: Optional[AsyncSession] = None) -> Compra | None:
        return await super().get_by_id(compra_id, session=session)

    async def get_by_proveedor(self, proveedor_id: int, session: Optional[AsyncSession] = None) -> list[Compra]:
        session = session or await self.get_session()
        result = await session.execute(
            select(Compra).where(Compra.proveedor_id == proveedor_id)
        )
        return result.scalars().all()

    async def update_compra(self, compra_id: int, compra_dto: CompraDTO, session: Optional[AsyncSession] = None) -> Compra | None:
        session = session or await self.get_session()
        compra = await self.get_by_id(compra_id, session=session)
        if compra:
            for field, value in compra_dto.model_dump(exclude_unset=True).items():
                setattr(compra, field, value)
            await session.commit()
            await session.refresh(compra)
            return compra
        return None

    async def delete_compra(self, compra_id: int, session: Optional[AsyncSession] = None) -> bool:
        session = session or await self.get_session()
        compra = await self.get_by_id(compra_id, session=session)
        if compra:
            await self.delete(compra, session=session)
            return True
        return False
    
    