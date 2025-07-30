# app/v1_0/services/credito_service.py

from typing import List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1_0.entities import CreditoDTO
from app.v1_0.models import Credito
from app.v1_0.repositories import CreditoRepository


class CreditoService:
    """
    Servicio para gestionar la entidad Credito. 
    Esta operación es independiente y no afecta saldos de bancos.
    """

    def __init__(self, credito_repository: CreditoRepository):
        """
        Inicializa el servicio con el repositorio de créditos.

        Args:
            credito_repository (CreditoRepository): Repositorio para CRUD de créditos.
        """
        self.credito_repo = credito_repository

    async def crear_credito(
        self,
        credito_dto: CreditoDTO,
        db: AsyncSession
    ) -> Credito:
        """
        Crea un nuevo crédito.

        Args:
            credito_dto (CreditoDTO): DTO con los datos del crédito a crear.
            db (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            Credito: La entidad Crédito recién persistida.
        """
        async with db.begin():
            credito = await self.credito_repo.create_credito(credito_dto, session=db)
        return credito

    async def obtener_credito(
        self,
        credito_id: int,
        db: AsyncSession
    ) -> Credito:
        """
        Recupera un crédito por su ID.

        Args:
            credito_id (int): ID del crédito a buscar.
            db (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            Credito: La entidad encontrada.

        Raises:
            HTTPException 404: Si no existe un crédito con ese ID.
        """
        credito = await self.credito_repo.get_by_id(credito_id, session=db)
        if not credito:
            raise HTTPException(status_code=404, detail="Crédito no encontrado")
        return credito

    async def listar_creditos(
        self,
        db: AsyncSession
    ) -> List[Credito]:
        """
        Recupera todos los créditos existentes.

        Args:
            db (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            List[Credito]: Lista de todas las entidades Crédito.
        """
        return await self.credito_repo.get_all(session=db)

    async def buscar_creditos(
        self,
        nombre: str,
        db: AsyncSession
    ) -> List[Credito]:
        """
        Busca créditos cuyo nombre contenga la cadena dada (case-insensitive).

        Args:
            nombre (str): Subcadena a buscar en el nombre del crédito.
            db (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            List[Credito]: Créditos que coinciden con el filtro.
        """
        return await self.credito_repo.get_by_nombre(nombre, session=db)

    async def actualizar_monto(
        self,
        credito_id: int,
        nuevo_monto: float,
        db: AsyncSession
    ) -> Credito:
        """
        Actualiza únicamente el monto de un crédito existente.

        Args:
            credito_id (int): ID del crédito a actualizar.
            nuevo_monto (float): Nuevo valor para el campo monto.
            db (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            Credito: La entidad Crédito actualizada.

        Raises:
            HTTPException 404: Si no existe un crédito con ese ID.
        """
        credito = await self.credito_repo.update_monto(credito_id, nuevo_monto, session=db)
        if not credito:
            raise HTTPException(status_code=404, detail="Crédito no encontrado")
        return credito

    async def eliminar_credito(
    self,
    credito_id: int,
    db: AsyncSession
    ) -> bool:
        async with db.begin():
            credito = await self.credito_repo.get_by_id(credito_id, session=db) 
            if not credito:
                raise HTTPException(status_code=404, detail="Crédito no encontrado")
            await self.credito_repo.delete(credito, session=db)
        return True
