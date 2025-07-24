from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.v1_0.models import Producto
from app.v1_0.entities import ProductoDTO
from app.v1_0.repositories import BaseRepository

class ProductoRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(Producto, db)

    async def create_producto(self, producto_dto: ProductoDTO) -> Producto:
        producto = Producto(**producto_dto.model_dump())
        return await self.create(producto)

    async def get_by_referencia(self, referencia: str) -> Producto | None:
        result = await self.db.execute(
            select(Producto).where(Producto.referencia == referencia)
        )
        return result.scalar_one_or_none()

    async def get_by_descripcion(self, descripcion: str) -> list[Producto]:
        result = await self.db.execute(
            select(Producto).where(Producto.descripcion.ilike(f"%{descripcion}%"))
        )
        return result.scalars().all()

    async def update_producto(self, producto_id: int, producto_dto: ProductoDTO) -> Producto | None:
        producto = await self.get_by_id(producto_id)
        if producto:
            for field, value in producto_dto.model_dump(exclude_unset=True).items():
                setattr(producto, field, value)
            await self.db.commit()
            await self.db.refresh(producto)
            return producto
        return None

    async def delete_producto(self, producto_id: int) -> bool:
        producto = await self.get_by_id(producto_id)
        if producto:
            await self.delete(producto)
            return True
        return False

    async def toggle_estado(self, producto_id: int) -> Producto | None:
        producto = await self.get_by_id(producto_id)
        if producto:
            producto.activo = not producto.activo
            await self.db.commit()
            await self.db.refresh(producto)
            return producto
        return None

    async def aumentar_cantidad(self, producto_id: int, cantidad: int) -> Producto | None:
        """
        Aumenta el stock disponible de un producto.

        Args:
            producto_id (int): ID del producto.
            cantidad (int): Unidades a aumentar.

        Returns:
            Producto actualizado o None si no existe.
        """
        producto = await self.get_by_id(producto_id)
        if producto:
            producto.cantidad = (producto.cantidad or 0) + cantidad
            await self.db.commit()
            await self.db.refresh(producto)
            return producto
        return None

    async def disminuir_cantidad(self, producto_id: int, cantidad: int) -> Producto | None:
        """
        Disminuye el stock disponible de un producto. No permite valores negativos.

        Args:
            producto_id (int): ID del producto.
            cantidad (int): Unidades a restar.

        Returns:
            Producto actualizado o None si no existe o si el stock es insuficiente.
        """
        producto = await self.get_by_id(producto_id)
        if producto and (producto.cantidad or 0) >= cantidad:
            producto.cantidad -= cantidad
            await self.db.commit()
            await self.db.refresh(producto)
            return producto
        return None