from sqlalchemy.ext.asyncio import AsyncSession
from typing import Generic, TypeVar, Type

ModelType = TypeVar("ModelType")

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_all(self):
        result = await self.db.execute(self.model.__table__.select())
        return result.scalars().all()

    async def get_by_id(self, id: int):
        return await self.db.get(self.model, id)

    async def create(self, obj: ModelType):
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj: ModelType):
        await self.db.delete(obj)
        await self.db.commit()
