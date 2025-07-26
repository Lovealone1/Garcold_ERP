from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable, TypeVar, Generic, Type, Optional
from contextlib import asynccontextmanager

T = TypeVar("T")

class BaseRepository(Generic[T]):
    def __init__(self, session_factory: Callable[[], AsyncSession], model_class: Type[T]):
        self._session_factory = session_factory
        self.model_class = model_class

    @property
    def db(self) -> AsyncSession:
        return self._session_factory()

    async def create(self, obj: T, session: Optional[AsyncSession] = None) -> T:
        session = session or self.db
        async with session:
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
        return obj

    async def delete(self, obj: T, session: Optional[AsyncSession] = None) -> None:
        session = session or self.db
        async with session:
            await session.delete(obj)
            await session.commit()

    async def get_by_id(self, obj_id: int, session: Optional[AsyncSession] = None) -> Optional[T]:
        session = session or self.db
        async with session:
            return await session.get(self.model_class, obj_id)

    async def get_all(self, session: Optional[AsyncSession] = None) -> list[T]:
        from sqlalchemy import select
        session = session or self.db
        async with session:
            result = await session.execute(select(self.model_class))
            return result.scalars().all()

    async def get_session(self) -> AsyncSession:
        return self._session_factory()
    
    @asynccontextmanager
    async def session_scope(self) -> AsyncSession:
        """
        Context manager asincrónico para manejar una sesión reutilizable y cerrarla automáticamente.
        """
        session = self._session_factory()
        try:
            yield session
        finally:
            await session.close()
