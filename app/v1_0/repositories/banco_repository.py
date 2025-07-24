from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.v1_0.models import Banco
from app.v1_0.entities import BancoDTO
from app.v1_0.repositories import BaseRepository


class BancoRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(Banco, db)

    async def create_banco(self, banco_dto: BancoDTO) -> Banco:
        banco = Banco(**banco_dto.model_dump())
        return await self.create(banco)

    async def get_by_nombre(self, nombre: str) -> Banco | None:
        result = await self.db.execute(
            select(Banco).where(Banco.nombre == nombre)
        )
        return result.scalar_one_or_none()

    async def update_saldo(self, banco_id: int, nuevo_saldo: float) -> Banco | None:
        """
        Actualiza el saldo de un banco y registra la fecha de actualización.

        Args:
            banco_id (int): ID del banco a actualizar.
            nuevo_saldo (float): Nuevo saldo a asignar.

        Returns:
            Banco actualizado o None si no existe.
        """
        banco = await self.get_by_id(banco_id)
        if banco:
            banco.saldo = nuevo_saldo
            banco.fecha_actualizacion = datetime.now()
            await self.db.commit()
            await self.db.refresh(banco)
            return banco
        return None

    async def delete_banco(self, banco_id: int) -> bool:
            banco = await self.get_by_id(banco_id)
            if banco:
                await self.delete(banco)
                return True
            return False
    
    async def _aumentar_saldo(self, banco_id: int, monto: float) -> Banco | None:
        """
        Aumenta el saldo del banco en la cantidad especificada.

        Args:
            banco_id (int): ID del banco.
            monto (float): Monto a aumentar.

        Returns:
            Banco actualizado o None si no existe.
        """
        banco = await self.get_by_id(banco_id)
        if banco:
            banco.saldo += monto
            banco.fecha_actualizacion = datetime.now()
            await self.db.commit()
            await self.db.refresh(banco)
            return banco
        return None

    async def _disminuir_saldo(self, banco_id: int, monto: float) -> Banco | None:
        """
        Disminuye el saldo del banco en la cantidad especificada.

        Args:
            banco_id (int): ID del banco.
            monto (float): Monto a disminuir.

        Returns:
            Banco actualizado o None si no existe o si el saldo es insuficiente.
        """
        banco = await self.get_by_id(banco_id)
        if banco and banco.saldo >= monto:
            banco.saldo -= monto
            banco.fecha_actualizacion = datetime.now()
            await self.db.commit()
            await self.db.refresh(banco)
            return banco
        return None