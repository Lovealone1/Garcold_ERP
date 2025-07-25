from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable, TypeVar, Generic, Type

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, session_factory: Callable[[], AsyncSession], model_class: Type[T]):
        self._session_factory = session_factory
        self.model_class = model_class

    @property
    def db(self) -> AsyncSession:
        return self._session_factory()

    async def create(self, obj: T) -> T:
        async with self.db as session:
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
        return obj

    async def delete(self, obj: T) -> None:
        async with self.db as session:
            await session.delete(obj)
            await session.commit()

    async def get_by_id(self, obj_id: int) -> T | None:
        async with self.db as session:
            return await session.get(self.model_class, obj_id)

    async def get_session(self) -> AsyncSession:
        return self._session_factory()