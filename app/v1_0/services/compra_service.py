# app/v1_0/services/compra_service.py

from datetime import datetime
from typing import List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1_0.entities import CompraDTO, DetalleCompraDTO
from app.v1_0.schemas.compra_schema import CompraResponse
from app.v1_0.models import Compra
from app.v1_0.repositories import (
    CompraRepository,
    DetalleCompraRepository,
    ProductoRepository,
    BancoRepository,
    ProveedorRepository,
    EstadoRepository
)

class CompraService:
    """
    Servicio que orquesta la lógica de negocio para el manejo de Compras:
     - Construcción de detalles
     - Registro (creación) de compras
     - Consulta de compras
     - Eliminación de compras y reversión de inventario/saldos
    """
    def __init__(
        self,
        compra_repository: CompraRepository,
        detalle_repository: DetalleCompraRepository,
        producto_repository: ProductoRepository,
        banco_repository: BancoRepository,
        proveedor_repository: ProveedorRepository,
        estado_repository: EstadoRepository
    ):
        self.compra_repository = compra_repository
        self.detalle_repository = detalle_repository
        self.producto_repository = producto_repository
        self.banco_repository = banco_repository
        self.proveedor_repository = proveedor_repository
        self.estado_repository = estado_repository

    def construir_detalles(self, carrito: List[dict]) -> List[DetalleCompraDTO]:
        """
        Transforma la lista de ítems recibida del frontend en DTOs de detalle de compra.

        Args:
            carrito: Lista de dicts con claves:
                - producto_id (int)
                - cantidad (int)
                - precio (float)

        Returns:
            Una lista de DetalleCompraDTO con los totales por ítem y compra_id = 0.
        """
        detalles: List[DetalleCompraDTO] = []
        for item in carrito:
            total = item.cantidad * item.precio
            detalles.append(DetalleCompraDTO(
                producto_id=item.producto_id,
                cantidad=item.cantidad,
                precio=item.precio,
                total=total,
                compra_id=0
            ))
        return detalles

    async def registrar_compra(
        self,
        proveedor_id: int,
        banco_id: int,
        estado_id: int,
        detalles: List[DetalleCompraDTO],
        db: AsyncSession
    ) -> CompraResponse:
        """
        Registra una nueva compra junto con sus detalles, ajusta inventario y saldos.

        Ejecuta todo dentro de una transacción atómica.

        Args:
            proveedor_id: ID del proveedor de la compra.
            banco_id: ID del banco para débito/crédito.
            estado_id: ID que indica si es compra a crédito o contado.
            detalles: Lista de DetalleCompraDTO sin IDs de compra.
            db: Sesión asíncrona de SQLAlchemy.

        Returns:
            CompraResponse: DTO listo para devolver al cliente con
                - id: nuevo ID de compra
                - proveedor, banco, estado: nombres resueltos
                - total, saldo, fecha

        Raises:
            HTTPException 404: Si algún producto o la compra no se encuentra.
        """
        async with db.begin():

            total_compra = 0.0
            for d in detalles:
                producto = await self.producto_repository.get_by_id(d.producto_id, session=db)
                if not producto:
                    raise HTTPException(404, f"Producto {d.producto_id} no encontrado")
                total_compra += d.total

            estado = await self.estado_repository.get_by_id(estado_id, session=db)
            es_credito = bool(estado and estado.nombre.lower() == "compra credito")
            saldo = total_compra if es_credito else 0.0

            compra_dto = CompraDTO(
                proveedor_id=proveedor_id,
                banco_id=banco_id,
                estado_id=estado_id,
                total=total_compra,
                saldo=saldo,
                fecha=datetime.now()
            )

            compra = await self.compra_repository.create_compra(compra_dto, session=db)

            detalles_con_id = [
                DetalleCompraDTO(
                    producto_id=d.producto_id,
                    cantidad=d.cantidad,
                    precio=d.precio,
                    total=d.total,
                    compra_id=compra.id
                ) for d in detalles
            ]
            await self.detalle_repository.bulk_insert_detalles(detalles_con_id, session=db)

            for d in detalles:
                await self.producto_repository.aumentar_cantidad(
                    d.producto_id, d.cantidad, session=db
                )

            if not es_credito:
                await self.banco_repository.disminuir_saldo(
                    banco_id, total_compra, session=db
                )
            proveedor = await self.proveedor_repository.get_by_id(compra.proveedor_id, session=db)
            banco     = await self.banco_repository.get_by_id(compra.banco_id, session=db)
            estado    = await self.estado_repository.get_by_id(compra.estado_id, session=db)
            return CompraResponse(
                id=compra.id,
                proveedor=proveedor.nombre if proveedor else "Desconocido",
                banco=banco.nombre if banco else "Desconocido",
                estado=estado.nombre if estado else "Desconocido",
                total=compra.total,
                saldo=compra.saldo,
                fecha=compra.fecha_compra
            )

    async def obtener_compra(
        self,
        compra_id: int,
        db: AsyncSession
    ) -> CompraResponse:
        """
        Recupera una compra por su ID y construye el DTO de respuesta.

        Args:
            compra_id: ID de la compra a consultar.
            db: Sesión asíncrona de SQLAlchemy.

        Returns:
            CompraResponse con todos los campos desplegados.

        Raises:
            HTTPException 404: Si la compra no existe.
        """
        compra = await self.compra_repository.get_by_id(compra_id, session=db)
        if not compra:
            raise HTTPException(404, "Compra no encontrada")

        proveedor = await self.proveedor_repository.get_by_id(compra.proveedor_id, session=db)
        banco     = await self.banco_repository.get_by_id(compra.banco_id, session=db)
        estado    = await self.estado_repository.get_by_id(compra.estado_id, session=db)

        return CompraResponse(
            id=compra.id,
            proveedor=proveedor.nombre if proveedor else "Desconocido",
            banco=banco.nombre if banco else "Desconocido",
            estado=estado.nombre if estado else "Desconocido",
            total=compra.total,
            saldo=compra.saldo,
            fecha=compra.fecha_compra
        )

    async def eliminar_compra(
    self,
    compra_id: int,
    db: AsyncSession
    ) -> bool:
        """
        Elimina una compra y revierte inventario y saldos asociados en una transacción.

        Args:
            compra_id: ID de la compra a eliminar.
            db: Sesión asíncrona de SQLAlchemy.

        Returns:
            True si la compra fue eliminada correctamente.

        Raises:
            HTTPException 404: Si la compra no existe.
        """
        async with db.begin():
            compra = await self.compra_repository.get_by_id(compra_id, session=db)
            if not compra:
                raise HTTPException(404, "Compra no encontrada")
            
            detalles   = await self.detalle_repository.get_by_compra_id(compra_id, session=db)
            estado     = await self.estado_repository.get_by_id(compra.estado_id, session=db)
            es_credito = bool(estado and estado.nombre.lower() == "compra credito")

            for d in detalles:
                await self.producto_repository.disminuir_cantidad(
                    d.producto_id, d.cantidad, session=db
                )

            if not es_credito:
                await self.banco_repository.aumentar_saldo(
                    compra.banco_id, compra.total, session=db
                )

            await self.detalle_repository.delete_by_compra(compra_id, session=db)
            await self.compra_repository.delete_compra(compra_id, session=db)

        return True

