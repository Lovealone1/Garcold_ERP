from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.v1_0.repositories.banco_repository import BancoRepository
from app.v1_0.schemas.banco_schema import BancoCreateSchema
from app.v1_0.entities import BancoDTO
from app.v1_0.models import Banco

class BancoService:
    def __init__(self, banco_repository: BancoRepository):
        self.banco_repository = banco_repository

    async def create_banco(self, banco_create: BancoCreateSchema, db: AsyncSession) -> Banco:
        """Crea banco."""
        async with db.begin():
            return await self.banco_repository.create_banco(banco_create, session=db)

    async def get_banco_by_id(self, banco_id: int, db: AsyncSession) -> Optional[Banco]:
        """Obtiene banco por ID."""
        async with db.begin():
            return await self.banco_repository.get_by_id(banco_id, session=db)

    async def get_all_bancos(self, db: AsyncSession) -> List[Banco]:
        """Lista todos los bancos."""
        async with db.begin():
            return await self.banco_repository.list_bancos(session=db)

    async def update_saldo(self, banco_id: int, nuevo_saldo: float, db: AsyncSession) -> Optional[Banco]:
        """Actualiza saldo."""
        async with db.begin():
            return await self.banco_repository.update_saldo(banco_id, nuevo_saldo, session=db)

    async def delete_banco(self, banco_id: int, db: AsyncSession) -> bool:
        """Elimina banco si saldo == 0."""
        async with db.begin():
            banco = await self.banco_repository.get_by_id(banco_id, session=db)
            if not banco:
                return False
            if banco.saldo > 0:
                raise ValueError("No se puede eliminar un banco con saldo mayor a 0.")
            return await self.banco_repository.delete_banco(banco_id, session=db)

    async def disminuir_saldo(self, banco_id: int, monto: float, db: AsyncSession) -> Banco:
        """Disminuye saldo con validaciones."""
        async with db.begin():
            banco = await self.banco_repository.get_by_id(banco_id, session=db)
            if not banco:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Banco no encontrado.")
            if banco.saldo < monto:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Saldo insuficiente: disponible {banco.saldo}, requerido {monto}"
                )
            return await self.banco_repository.disminuir_saldo(banco_id, monto, session=db)

    async def aumentar_saldo(self, banco_id: int, monto: float, db: AsyncSession) -> Banco:
        """Aumenta saldo con validaciones."""
        if monto <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El monto a aumentar debe ser mayor a cero."
            )
        async with db.begin():
            banco = await self.banco_repository.get_by_id(banco_id, session=db)
            if not banco:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Banco no encontrado.")
            return await self.banco_repository.aumentar_saldo(banco_id, monto, session=db)
