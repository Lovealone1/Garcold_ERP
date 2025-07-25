from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable

from app.v1_0.models import Venta
from app.v1_0.repositories import BaseRepository
from app.v1_0.entities import VentaDTO

class VentaRepository(BaseRepository):
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        super().__init__(session_factory, Venta)

    async def create_venta(self, venta_dto: VentaDTO) -> Venta:
        venta = Venta(**venta_dto.model_dump())
        return await self.create(venta)

    async def get_by_id(self, venta_id: int) -> Venta | None:
        return await super().get_by_id(venta_id)

    async def get_all(self) -> list[Venta]:
        return await super().get_all()

    async def update_venta(self, venta_id: int, venta_dto: VentaDTO) -> Venta | None:
        venta = await self.get_by_id(venta_id)
        if venta:
            for field, value in venta_dto.model_dump(exclude_unset=True).items():
                setattr(venta, field, value)
            await self.db.commit()
            await self.db.refresh(venta)
            return venta
        return None

    async def delete_venta(self, venta_id: int) -> bool:
        venta = await self.get_by_id(venta_id)
        if venta:
            await self.delete(venta)
            return True
        return False
