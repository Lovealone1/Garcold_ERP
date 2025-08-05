# app/v1_0/services/utilidad_service.py

from typing import List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.v1_0.repositories.utiliadad_repository import UtilidadRepository
from app.v1_0.models import Utilidad

PAGE_SIZE = 10

class UtilidadService:
    def __init__(self, utilidad_repository: UtilidadRepository):
        self.utilidad_repository = utilidad_repository

    async def listar_utilidades(
        self,
        page: int,
        db: AsyncSession
    ) -> List[Utilidad]:
        """
        Lista todas las utilidades, PAGE_SIZE por página.
        """
        if page < 1:
            raise HTTPException(status_code=400, detail="page debe ser >= 1")
        offset = (page - 1) * PAGE_SIZE
        async with db.begin():
            return await self.utilidad_repository.list_paginated(
                offset,
                PAGE_SIZE,
                session=db
            )

    async def listar_utilidades_por_rango(
        self,
        fecha_inicio: datetime,
        fecha_fin: datetime,
        page: int,
        db: AsyncSession
    ) -> List[Utilidad]:
        """
        Lista utilidades entre fecha_inicio y fecha_fin, PAGE_SIZE por página.
        """
        if fecha_fin < fecha_inicio:
            raise HTTPException(status_code=400, detail="fecha_fin debe ser >= fecha_inicio")
        if page < 1:
            raise HTTPException(status_code=400, detail="page debe ser >= 1")
        offset = (page - 1) * PAGE_SIZE
        async with db.begin():
            return await self.utilidad_repository.list_by_rango_paginated(
                fecha_inicio,
                fecha_fin,
                offset,
                PAGE_SIZE,
                session=db
            )
