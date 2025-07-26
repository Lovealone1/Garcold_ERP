from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Callable, Optional

from app.v1_0.models import Proveedor
from app.v1_0.repositories import BaseRepository
from app.v1_0.entities import ProveedorDTO

class ProveedorRepository(BaseRepository):
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        super().__init__(session_factory, Proveedor)

    async def create_proveedor(self, proveedor_dto: ProveedorDTO, session: Optional[AsyncSession] = None) -> Proveedor:
        proveedor = Proveedor(**proveedor_dto.model_dump())
        return await self.create(proveedor, session=session)

    async def get_by_cc_nit(self, cc_nit: str, session: Optional[AsyncSession] = None) -> Proveedor | None:
        session = session or await self.get_session()
        result = await session.execute(
            select(Proveedor).where(Proveedor.cc_nit == str(cc_nit))
        )
        return result.scalar_one_or_none()

    async def get_by_nombre(self, nombre: str, session: Optional[AsyncSession] = None) -> list[Proveedor]:
        session = session or await self.get_session()
        result = await session.execute(
            select(Proveedor).where(Proveedor.nombre.ilike(f"%{nombre}%"))
        )
        return result.scalars().all()

    async def update_proveedor(self, proveedor_id: int, proveedor_dto: ProveedorDTO, session: Optional[AsyncSession] = None) -> Proveedor | None:
        session = session or await self.get_session()
        proveedor = await self.get_by_id(proveedor_id, session=session)
        if proveedor:
            for field, value in proveedor_dto.model_dump(exclude_unset=True).items():
                setattr(proveedor, field, value)
            await session.commit()
            await session.refresh(proveedor)
            return proveedor
        return None

    async def delete_proveedor(self, proveedor_id: int, session: Optional[AsyncSession] = None) -> bool:
        session = session or await self.get_session()
        proveedor = await self.get_by_id(proveedor_id, session=session)
        if proveedor:
            await self.delete(proveedor, session=session)
            return True
        return False
