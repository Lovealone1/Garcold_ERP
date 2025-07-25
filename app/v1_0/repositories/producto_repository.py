from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Callable

from app.v1_0.models import Producto
from app.v1_0.entities import ProductoDTO
from app.v1_0.repositories.base_repository import BaseRepository  


class ProductoRepository(BaseRepository[Producto]):
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        super().__init__(session_factory=session_factory, model_class=Producto)

    async def create_producto(self, producto_dto: ProductoDTO, session: AsyncSession | None = None) -> Producto:
        producto = Producto(**producto_dto.model_dump())
        return await self.create(producto, session=session)

    async def get_by_id(self, producto_id: int, session: AsyncSession | None = None) -> Producto | None:
        session = session or await self.get_session()
        result = await session.execute(select(Producto).where(Producto.id == producto_id))
        return result.scalar_one_or_none()

    async def get_by_referencia(self, referencia: str, session: AsyncSession | None = None) -> Producto | None:
        session = session or await self.get_session()
        result = await session.execute(select(Producto).where(Producto.referencia == referencia))
        return result.scalar_one_or_none()

    async def get_by_descripcion(self, descripcion: str, session: AsyncSession | None = None) -> list[Producto]:
        session = session or await self.get_session()
        result = await session.execute(select(Producto).where(Producto.descripcion.ilike(f"%{descripcion}%")))
        return result.scalars().all()

    async def update_producto(self, producto_id: int, producto_dto: ProductoDTO, session: AsyncSession | None = None) -> Producto | None:
        session = session or await self.get_session()
        producto = await self.get_by_id(producto_id, session=session)
        if producto:
            for field, value in producto_dto.model_dump(exclude_unset=True).items():
                setattr(producto, field, value)
            await session.commit()
            await session.refresh(producto)
            return producto
        return None

    async def delete_producto(self, producto_id: int, session: AsyncSession | None = None) -> bool:
        session = session or await self.get_session()
        producto = await self.get_by_id(producto_id, session=session)
        if producto:
            await session.delete(producto)
            await session.commit()
            return True
        return False

    async def toggle_estado(self, producto_id: int, session: AsyncSession | None = None) -> Producto | None:
        session = session or await self.get_session()
        producto = await self.get_by_id(producto_id, session=session)
        if producto:
            producto.activo = not producto.activo
            await session.commit()
            await session.refresh(producto)
            return producto
        return None

    async def aumentar_cantidad(self, producto_id: int, cantidad: int, session: AsyncSession | None = None) -> Producto | None:
        session = session or await self.get_session()
        producto = await self.get_by_id(producto_id, session=session)
        if producto:
            producto.cantidad = (producto.cantidad or 0) + cantidad
            await session.commit()
            await session.refresh(producto)
            return producto
        return None

    async def disminuir_cantidad(self, producto_id: int, cantidad: int, session: AsyncSession | None = None) -> Producto | None:
        session = session or await self.get_session()
        producto = await self.get_by_id(producto_id, session=session)
        if producto and (producto.cantidad or 0) >= cantidad:
            producto.cantidad -= cantidad
            await session.commit()
            await session.refresh(producto)
            return producto
        return None
