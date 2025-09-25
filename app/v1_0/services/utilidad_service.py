from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from math import ceil
from typing import List

from app.v1_0.repositories import UtilidadRepository, DetalleUtilidadRepository, ProductoRepository
from app.v1_0.models import Utilidad
from app.v1_0.entities import UtilidadListDTO, UtilidadPageDTO, DetalleUtilidadDTO

PAGE_SIZE = 12

class UtilidadService:
    def __init__(self, utilidad_repository: UtilidadRepository, detalle_utilidad_repository: DetalleUtilidadRepository,producto_repository: ProductoRepository):
        self.utilidad_repository = utilidad_repository
        self.detalle_utilidad_repository = detalle_utilidad_repository
        self.producto_repository = producto_repository

    async def listar_utilidades(self, page: int, db: AsyncSession) -> UtilidadPageDTO:
        """
        Lista utilidades paginadas con metadatos, orden ascendente por id.
        """
        offset = (page - 1) * PAGE_SIZE
        async with db.begin():
            items, total = await self.utilidad_repository.list_paginated(
                offset=offset, limit=PAGE_SIZE, session=db
            )

        total = int(total or 0)
        total_pages = max(1, ceil(total / PAGE_SIZE)) if total else 1

        return UtilidadPageDTO(
            items=[
                UtilidadListDTO(
                    id=u.id,
                    venta_id=u.venta_id,
                    utilidad=u.utilidad,
                    fecha=u.fecha,
                )
                for u in items
            ],
            page=page,
            page_size=PAGE_SIZE,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )

    async def obtener_por_venta_id(
        self,
        venta_id: int,
        db: AsyncSession
    ) -> Utilidad:
        """
        Retorna la utilidad asociada a una venta_id.
        Lanza HTTPException 404 si no existe.
        """
        async with db.begin():
            utilidad = await self.utilidad_repository.get_utilidad_by_venta_id(
                venta_id=venta_id, session=db
            )
            if not utilidad:
                raise HTTPException(status_code=404, detail="Utilidad no encontrada para la venta indicada")
            return utilidad

    async def obtener_detalles_por_venta(
        self,
        venta_id: int,
        db: AsyncSession
    ) -> List[DetalleUtilidadDTO]:
        """
        Retorna todos los DetalleUtilidad asociados a la venta,
        mapeados a DTO incluyendo referencia y descripcion del producto.
        """
        async with db.begin():
            rows = await self.detalle_utilidad_repository.get_by_venta(
                venta_id=venta_id, session=db
            )

            dtos: List[DetalleUtilidadDTO] = []
            for r in rows:
                prod = await self.producto_repository.get_by_id(r.producto_id, session=db)
                referencia = getattr(prod, "referencia", None) if prod else None
                descripcion = getattr(prod, "descripcion", None) if prod else None

                total_utilidad = (
                    (float(r.precio_venta) - float(r.precio_compra)) * int(r.cantidad)
                    if r.precio_venta is not None and r.precio_compra is not None
                    else 0.0
                )

                dtos.append(
                    DetalleUtilidadDTO(
                        venta_id=r.venta_id,
                        producto_id=r.producto_id,
                        referencia=referencia,
                        descripcion=descripcion,
                        cantidad=int(r.cantidad),
                        precio_compra=float(r.precio_compra),
                        precio_venta=float(r.precio_venta),
                        total_utilidad=float(total_utilidad),
                    )
                )

        return dtos
        
    