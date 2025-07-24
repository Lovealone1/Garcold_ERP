from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.v1_0.repositories import BancoRepository
from app.v1_0.entities import BancoDTO
from app.v1_0.models import Banco


class BancoService:
    def __init__(self, db: AsyncSession):
        self.banco_repository = BancoRepository(db)

    async def create_banco(self, banco_dto: BancoDTO) -> Banco:
        """
        Crea un nuevo banco.

        Args:
            banco_dto (BancoDTO): Datos del banco a registrar.

        Returns:
            Banco: Instancia del banco creado.
        """
        return await self.banco_repository.create_banco(banco_dto)

    async def get_banco_by_id(self, banco_id: int) -> Banco | None:
        """
        Consulta un banco por su ID.

        Args:
            banco_id (int): ID del banco.

        Returns:
            Banco o None si no existe.
        """
        return await self.banco_repository.get_by_id(banco_id)

    async def get_all_bancos(self) -> list[Banco]:
        """
        Retorna todos los bancos registrados.

        Returns:
            list[Banco]: Lista de bancos.
        """
        return await self.banco_repository.get_all()

    async def update_saldo(self, banco_id: int, nuevo_saldo: float) -> Banco | None:
        """
        Actualiza el saldo de un banco y su fecha de modificación.

        Args:
            banco_id (int): ID del banco.
            nuevo_saldo (float): Nuevo valor del saldo.

        Returns:
            Banco actualizado o None si no existe.
        """
        return await self.banco_repository.update_saldo(banco_id, nuevo_saldo)

    async def delete_banco(self, banco_id: int) -> bool:
        """
        Elimina un banco si su saldo es igual a 0.

        Args:
            banco_id (int): ID del banco.

        Returns:
            bool: True si fue eliminado, False si no existe o no se puede eliminar.

        Raises:
            ValueError: Si el banco tiene un saldo mayor a 0.
        """
        banco = await self.banco_repository.get_by_id(banco_id)
        if not banco:
            return False
        if banco.saldo > 0:
            raise ValueError("No se puede eliminar un banco con saldo mayor a 0.")
        return await self.banco_repository.delete_banco(banco_id)

    async def disminuir_saldo(self, banco_id: int, monto: float) -> Banco:
            """
            Disminuye el saldo del banco validando que haya suficiente saldo disponible.

            Args:
                banco_id (int): ID del banco.
                monto (float): Monto a disminuir.

            Raises:
                HTTPException: Si el banco no existe o el saldo es insuficiente.

            Returns:
                Banco actualizado.
            """
            banco = await self.banco_repository.get_by_id(banco_id)
            if not banco:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Banco no encontrado.")

            if banco.saldo < monto:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Saldo insuficiente: disponible {banco.saldo}, requerido {monto}"
                )

            return await self.banco_repository._disminuir_saldo(banco_id, monto)
    
    async def aumentar_saldo(self, banco_id: int, monto: float) -> Banco:
        """
        Aumenta el saldo de un banco validando el monto.

        Args:
            banco_id (int): ID del banco.
            monto (float): Monto a aumentar.

        Raises:
            HTTPException: Si el banco no existe o el monto es inválido.

        Returns:
            Banco actualizado.
        """
        if monto <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El monto a aumentar debe ser mayor a cero."
            )

        banco = await self.banco_repository.get_by_id(banco_id)
        if not banco:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Banco no encontrado.")

        return await self.banco_repository._aumentar_saldo(banco_id, monto)