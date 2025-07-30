# app/v1_0/repositories/categoria_gastos_repository.py

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1_0.models import CategoriaGastos
from app.v1_0.entities import CategoriaGastosDTO
from .base_repository import BaseRepository


class CategoriaGastosRepository(BaseRepository[CategoriaGastos]):
    """
    Repositorio para operaciones CRUD sobre la tabla categoria_gastos.
    """

    def __init__(self):
        super().__init__(CategoriaGastos)

    async def create_categoria(
        self,
        dto: CategoriaGastosDTO,
        session: AsyncSession
    ) -> CategoriaGastos:
        """
        Crea una nueva categoría de gasto a partir del DTO y hace flush para asignar su ID.
        """
        categoria = CategoriaGastos(**dto.model_dump())
        await self.add(categoria, session)
        return categoria

    async def get_by_id(
        self,
        categoria_id: int,
        session: AsyncSession
    ) -> Optional[CategoriaGastos]:
        """
        Recupera una categoría por su ID.
        """
        return await super().get_by_id(categoria_id, session=session)

    async def get_all(
        self,
        session: AsyncSession
    ) -> List[CategoriaGastos]:
        """
        Recupera todas las categorías de gasto.
        """
        return await super().get_all(session=session)

    async def get_by_nombre(
        self,
        nombre: str,
        session: AsyncSession
    ) -> Optional[CategoriaGastos]:
        """
        Recupera una categoría por su nombre exacto.
        """
        stmt = select(CategoriaGastos).where(CategoriaGastos.nombre == nombre)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_categoria(
        self,
        categoria_id: int,
        dto: CategoriaGastosDTO,
        session: AsyncSession
    ) -> Optional[CategoriaGastos]:
        """
        Actualiza los campos de una categoría existente según el DTO.
        """
        categoria = await self.get_by_id(categoria_id, session)
        if not categoria:
            return None

        for field, value in dto.model_dump(exclude_unset=True).items():
            setattr(categoria, field, value)

        await self.update(categoria, session)
        return categoria

    async def delete_categoria(
        self,
        categoria_id: int,
        session: AsyncSession
    ) -> bool:
        """
        Elimina una categoría de gasto por su ID; retorna True si existía.
        """
        categoria = await self.get_by_id(categoria_id, session)
        if not categoria:
            return False

        await self.delete(categoria, session)
        return True
