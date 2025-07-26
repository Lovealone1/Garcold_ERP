# app/v1_0/repositories/base.py

from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

T = TypeVar("T")

class BaseRepository(Generic[T]):
    """
    Repositorio base que expone operaciones CRUD básicas sobre una entidad T.
    No maneja sesiones ni commits: todo se hace con la misma AsyncSession pasada desde fuera.
    """
    def __init__(self, model_class: Type[T]):
        self.model_class = model_class

    async def add(self, entity: T, session: AsyncSession) -> T:
        """
        Agrega una nueva entidad al contexto y hace flush para asignar PK.
        No hace commit.
        """
        session.add(entity)
        await session.flush()
        return entity

    async def get_by_id(self, id: int, session: AsyncSession) -> Optional[T]:
        """
        Recupera una entidad por su PK.
        """
        return await session.get(self.model_class, id)

    async def get_all(self, session: AsyncSession) -> List[T]:
        """
        Trae todas las instancias de la entidad.
        """
        result = await session.execute(select(self.model_class))
        return result.scalars().all()

    async def update(self, entity: T, session: AsyncSession) -> T:
        """
        Marca la entidad como modificada y hace flush de los cambios.
        """
        await session.flush()
        return entity

    async def delete(self, entity: T, session: AsyncSession) -> None:
        """
        Elimina la entidad y hace flush.
        """
        await session.delete(entity)
        await session.flush()
