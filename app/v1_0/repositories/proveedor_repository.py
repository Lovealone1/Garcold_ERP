from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.v1_0.models import Proveedor
from app.v1_0.repositories import BaseRepository
from app.v1_0.entities import ProveedorDTO

class ProveedorRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(Proveedor, db)

    async def create_proveedor(self, proveedor_dto: ProveedorDTO) -> Proveedor:
        proveedor = Proveedor(**proveedor_dto.model_dump())
        return await self.create(proveedor)

    async def get_by_cc_nit(self, cc_nit: str) -> Proveedor | None:
        result = await self.db.execute(
            select(Proveedor).where(Proveedor.cc_nit == str(cc_nit))
        )
        return result.scalar_one_or_none()

    async def get_by_nombre(self, nombre: str) -> list[Proveedor]:
        result = await self.db.execute(
            select(Proveedor).where(Proveedor.nombre.ilike(f"%{nombre}%"))
        )
        return result.scalars().all()

    async def update_proveedor(self, proveedor_id: int, proveedor_dto: ProveedorDTO) -> Proveedor | None:
        proveedor = await self.get_by_id(proveedor_id)
        if proveedor:
            for field, value in proveedor_dto.model_dump(exclude_unset=True).items():
                setattr(proveedor, field, value)
            await self.db.commit()
            await self.db.refresh(proveedor)
            return proveedor
        return None

    async def delete_proveedor(self, proveedor_id: int) -> bool:
        proveedor = await self.get_by_id(proveedor_id)
        if proveedor:
            await self.delete(proveedor)
            return True
        return False
