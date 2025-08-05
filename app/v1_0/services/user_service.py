from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.v1_0.entities import UserDTO
from app.v1_0.repositories.user_repository import UserRepository
from app.utils.security import verify_password, get_password_hash

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.repo = user_repository

    async def register_user(
        self,
        username: str,
        plain_password: str,
        db: AsyncSession
    ):
        """
        Crea un usuario nuevo con la contraseña hasheada.
        """
        async with db.begin():
            existing = await self.repo.get_by_username(username, session=db)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El usuario ya existe"
                )
            hashed = get_password_hash(plain_password)

            dto = UserDTO(
                username=username,
                hashed_password=hashed,
                is_active=True
            )

            
            user = await self.repo.create_user(dto, session=db)

        return user

    async def authenticate(
        self,
        username: str,
        password: str,
        db: AsyncSession              
    ):
        """
        Verifica que el usuario exista y que la contraseña coincida.
        """
        user = await self.repo.get_by_username(username, session=db)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        return user
