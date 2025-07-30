# app/v1_0/services/inversion_service.py

from typing import List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1_0.entities import InversionDTO
from app.v1_0.models import Inversion
from app.v1_0.repositories import InversionRepository


class InversionService:
    """
    Servicio para gestionar la entidad Inversion.
    Cada operación se ejecuta sobre una AsyncSession proporcionada por el router.
    """

    def __init__(self, inversion_repository: InversionRepository):
        """
        Inicializa el servicio con el repositorio de inversiones.

        Args:
            inversion_repository (InversionRepository): Repositorio para CRUD de inversiones.
        """
        self.inversion_repo = inversion_repository

    async def crear_inversion(
        self,
        inversion_dto: InversionDTO,
        db: AsyncSession
    ) -> Inversion:
        """
        Crea una nueva inversión.

        Args:
            inversion_dto (InversionDTO): DTO con los datos de la inversión a crear.
            db (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            Inversion: La entidad Inversion recién persistida.
        """
        async with db.begin():
            inversion = await self.inversion_repo.create_inversion(
                inversion_dto, session=db
            )
        return inversion

    async def obtener_inversion(
        self,
        inversion_id: int,
        db: AsyncSession
    ) -> Inversion:
        """
        Recupera una inversión por su ID.

        Args:
            inversion_id (int): ID de la inversión a buscar.
            db (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            Inversion: La entidad encontrada.

        Raises:
            HTTPException 404: Si no existe una inversión con ese ID.
        """
        inversion = await self.inversion_repo.get_by_id(inversion_id, session=db)
        if not inversion:
            raise HTTPException(status_code=404, detail="Inversión no encontrada")
        return inversion

    async def listar_inversiones(
        self,
        db: AsyncSession
    ) -> List[Inversion]:
        """
        Recupera todas las inversiones existentes.

        Args:
            db (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            List[Inversion]: Lista de todas las entidades Inversion.
        """
        return await self.inversion_repo.get_all(session=db)

    async def buscar_inversiones(
        self,
        nombre: str,
        db: AsyncSession
    ) -> List[Inversion]:
        """
        Busca inversiones cuyo nombre contenga la cadena dada (case-insensitive).

        Args:
            nombre (str): Subcadena a buscar en el nombre de la inversión.
            db (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            List[Inversion]: Inversiones que coinciden con el filtro.
        """
        return await self.inversion_repo.get_by_nombre(nombre, session=db)

    async def actualizar_saldo(
        self,
        inversion_id: int,
        nuevo_saldo: float,
        db: AsyncSession
    ) -> Inversion:
        """
        Actualiza únicamente el saldo de una inversión existente.

        Args:
            inversion_id (int): ID de la inversión a actualizar.
            nuevo_saldo (float): Nuevo valor para el campo saldo.
            db (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            Inversion: La entidad Inversion actualizada.

        Raises:
            HTTPException 404: Si no existe una inversión con ese ID.
        """
        inversion = await self.inversion_repo.update_saldo(
            inversion_id, nuevo_saldo, session=db
        )
        if not inversion:
            raise HTTPException(status_code=404, detail="Inversión no encontrada")
        return inversion

    async def eliminar_inversion(
        self,
        inversion_id: int,
        db: AsyncSession
    ) -> bool:
        """
        Elimina una inversión por su ID.

        Args:
            inversion_id (int): ID de la inversión a eliminar.
            db (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            bool: True si la inversión existía y fue eliminada.

        Raises:
            HTTPException 404: Si no existe una inversión con ese ID.
        """
        async with db.begin():
            inversion = await self.inversion_repo.get_by_id(inversion_id, session=db)
            if not inversion:
                raise HTTPException(status_code=404, detail="Inversión no encontrada")
            await self.inversion_repo.delete_inversion(inversion_id, session=db)
        return True
