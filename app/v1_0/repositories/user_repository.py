from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1_0.models import User  
from .base_repository import BaseRepository
from app.v1_0.entities import UserDTO  

class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    async def get_by_username(
        self,
        username: str,
        session: AsyncSession
    ) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(
        self,
        dto: UserDTO,
        session: AsyncSession
    ) -> User:
        user = User(**dto.model_dump())
        await self.add(user, session)
        return user