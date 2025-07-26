from datetime import datetime
from typing import List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1_0.entities import VentaDTO, DetalleVentaDTO, DetalleUtilidadDTO, UtilidadDTO
from app.v1_0.schemas.venta_schema import VentaResponse
from app.v1_0.repositories import (
    VentaRepository,
    DetalleVentaRepository,
    ProductoRepository,
    ClienteRepository,
    EstadoRepository,
    DetalleUtilidadRepository,
    UtilidadRepository,
    BancoRepository
)

class VentaService:
    """
    Servicio que orquesta la lógica de negocio para el manejo de Ventas:
      - Construcción de detalles de venta
      - Finalización de venta (creación de venta, detalles, ajustes de inventario y saldo)
      - Cálculo y registro de utilidades
      - Consulta de ventas
      - Eliminación de ventas y reversión de inventario y saldos
    """
    def __init__(
        self,
        venta_repository: VentaRepository,
        detalle_repository: DetalleVentaRepository,
        producto_repository: ProductoRepository,
        cliente_repository: ClienteRepository,
        estado_repository: EstadoRepository,
        detalle_utilidad_repository: DetalleUtilidadRepository,
        utilidad_repository: UtilidadRepository,
        banco_repository: BancoRepository
    ):
        self.venta_repository = venta_repository
        self.detalle_repository = detalle_repository
        self.producto_repository = producto_repository
        self.cliente_repository = cliente_repository
        self.estado_repository = estado_repository
        self.detalle_utilidad_repository = detalle_utilidad_repository
        self.utilidad_repository = utilidad_repository
        self.banco_repository = banco_repository

    def agregar_detalle_venta(self, carrito: List[dict]) -> List[DetalleVentaDTO]:
        """
        Construye una lista de DetalleVentaDTO a partir del carrito enviado por el frontend.

        Args:
            carrito: Lista de objetos dict con campos:
                - producto_id (int)
                - cantidad (int)
                - precio_producto (float)

        Returns:
            List[DetalleVentaDTO]: Detalles con el cálculo de total por línea y venta_id = 0.
        """
        detalles = []
        for item in carrito:
            total = item.cantidad * item.precio_producto
            detalles.append(DetalleVentaDTO(
                producto_id=item.producto_id,
                cantidad=item.cantidad,
                precio_producto=item.precio_producto,
                total=total,
                venta_id=0
            ))
        return detalles

    async def finalizar_venta(
        self,
        cliente_id: int,
        banco_id: int,
        estado_id: int,
        detalles: List[DetalleVentaDTO],
        db: AsyncSession
    ) -> VentaResponse:
        """
        Finaliza una venta: valida stock, crea la venta y sus detalles,
        ajusta inventario y saldos, calcula y registra utilidades.

        Todo se ejecuta en una transacción atómica.

        Args:
            cliente_id: ID del cliente que realiza la compra.
            banco_id: ID del banco para débito o crédito.
            estado_id: ID que determina si es venta a crédito o contado.
            detalles: Lista de DetalleVentaDTO con los productos y precios.
            db: Sesión asíncrona de SQLAlchemy.

        Returns:
            VentaResponse: DTO con datos de la venta (id, cliente, banco, estado, total, saldo_restante, fecha).

        Raises:
            HTTPException 404: Si algún producto no existe.
            HTTPException 400: Si no hay suficiente stock para algún producto.
        """
        async with db.begin():
            total_venta = 0.0
            for d in detalles:
                producto = await self.producto_repository.get_by_id(d.producto_id, session=db)
                if not producto:
                    raise HTTPException(404, f"Producto {d.producto_id} no encontrado")
                if (producto.cantidad or 0) < d.cantidad:
                    raise HTTPException(400, f"Stock insuficiente para producto {producto.referencia}")
                total_venta += d.total

            estado = await self.estado_repository.get_by_id(estado_id, session=db)
            es_credito = bool(estado and estado.nombre.lower() == "venta credito")
            saldo_restante = total_venta if es_credito else 0.0

            venta_dto = VentaDTO(
                cliente_id=cliente_id,
                banco_id=banco_id,
                total=total_venta,
                estado_id=estado_id,
                saldo_restante=saldo_restante,
                fecha=datetime.now()
            )

            venta = await self.venta_repository.create_venta(venta_dto, session=db)

            detalles_con_id = [
                DetalleVentaDTO(
                    producto_id=d.producto_id,
                    cantidad=d.cantidad,
                    precio_producto=d.precio_producto,
                    total=d.total,
                    venta_id=venta.id
                ) for d in detalles
            ]
            await self.detalle_repository.bulk_insert_detalles(detalles_con_id, session=db)

            for d in detalles:
                await self.producto_repository.disminuir_cantidad(
                    d.producto_id, d.cantidad, session=db
                )

            if es_credito:
                cliente = await self.cliente_repository.get_by_id(cliente_id, session=db)
                if cliente:
                    nuevo_saldo = (cliente.saldo or 0) + total_venta
                    await self.cliente_repository.update_saldo(cliente_id, nuevo_saldo, session=db)
            else:
                banco = await self.banco_repository.get_by_id(banco_id, session=db)
                if banco:
                    nuevo_saldo = (banco.saldo or 0) + total_venta
                    await self.banco_repository.update_saldo(banco_id, nuevo_saldo, session=db)

            detalle_utilidades = await self._calcular_detalle_utilidad(detalles_con_id, session=db)
            await self.detalle_utilidad_repository.bulk_insert_detalles(detalle_utilidades, session=db)

            utilidad_total = sum(d.total_utilidad for d in detalle_utilidades)
            utilidad_dto = UtilidadDTO(venta_id=venta.id, utilidad=utilidad_total)
            await self.utilidad_repository.create_utilidad(utilidad_dto, session=db)

            cliente = await self.cliente_repository.get_by_id(cliente_id, session=db)
            banco    = await self.banco_repository.get_by_id(banco_id, session=db)

        return VentaResponse(
            id=venta.id,
            cliente=cliente.nombre if cliente else "Desconocido",
            banco=banco.nombre if banco else "Desconocido",
            estado=estado.nombre if estado else "Desconocido",
            total=venta.total,
            saldo_restante=venta.saldo_restante,
            fecha=venta.fecha
        )

    async def _calcular_detalle_utilidad(
        self,
        detalles: List[DetalleVentaDTO],
        session: AsyncSession
    ) -> List[DetalleUtilidadDTO]:
        """
        Construye la lista de DetalleUtilidadDTO calculando la utilidad por línea.

        Args:
            detalles: DetalleVentaDTO con la información de la venta.
            session: Sesión SQLAlchemy para obtener precio de compra.

        Returns:
            List[DetalleUtilidadDTO]: Detalles de utilidad listos para insertar.
        """
        resultado: List[DetalleUtilidadDTO] = []
        for d in detalles:
            producto = await self.producto_repository.get_by_id(d.producto_id, session=session)
            if not producto:
                raise HTTPException(404, f"Producto {d.producto_id} no encontrado")
            utilidad_unitaria = d.precio_producto - producto.precio_compra
            total_utilidad = utilidad_unitaria * d.cantidad
            resultado.append(DetalleUtilidadDTO(
                venta_id=d.venta_id,
                producto_id=d.producto_id,
                cantidad=d.cantidad,
                precio_compra=producto.precio_compra,
                precio_venta=d.precio_producto,
                total_utilidad=total_utilidad
            ))
        return resultado

    async def obtener_venta(
        self,
        venta_id: int,
        db: AsyncSession
    ) -> VentaResponse:
        """
        Obtiene una venta y construye el DTO de respuesta.

        Args:
            venta_id: ID de la venta.
            db: Sesión asíncrona de SQLAlchemy.

        Returns:
            VentaResponse: Datos completos de la venta.

        Raises:
            HTTPException 404: Si la venta no existe.
        """
        venta = await self.venta_repository.get_by_id(venta_id, session=db)
        if not venta:
            raise HTTPException(404, "Venta no encontrada")

        cliente = await self.cliente_repository.get_by_id(venta.cliente_id, session=db)
        banco    = await self.banco_repository.get_by_id(venta.banco_id, session=db)
        estado   = await self.estado_repository.get_by_id(venta.estado_id, session=db)

        return VentaResponse(
            id=venta.id,
            cliente=cliente.nombre if cliente else "Desconocido",
            banco=banco.nombre if banco else "Desconocido",
            estado=estado.nombre if estado else "Desconocido",
            total=venta.total,
            saldo_restante=venta.saldo_restante,
            fecha=venta.fecha
        )

    async def eliminar_venta(
        self,
        venta_id: int,
        db: AsyncSession
    ) -> None:
        """
        Elimina una venta y revierte inventario, saldos y utilidades en una transacción.

        Args:
            venta_id: ID de la venta a eliminar.
            db: Sesión asíncrona de SQLAlchemy.

        Raises:
            HTTPException 404: Si la venta no existe.
        """
        async with db.begin():
            venta = await self.venta_repository.get_by_id(venta_id, session=db)
            if not venta:
                raise HTTPException(404, "Venta no encontrada")

            detalles = await self.detalle_repository.get_by_venta_id(venta_id, session=db)
            estado   = await self.estado_repository.get_by_id(venta.estado_id, session=db)
            es_credito = bool(estado and estado.nombre.lower() == "venta credito")

            for d in detalles:
                await self.producto_repository.aumentar_cantidad(
                    d.producto_id, d.cantidad, session=db
                )

            if es_credito:
                cliente = await self.cliente_repository.get_by_id(venta.cliente_id, session=db)
                if cliente:
                    nuevo_saldo = max((cliente.saldo or 0) - venta.total, 0)
                    await self.cliente_repository.update_saldo(cliente.id, nuevo_saldo, session=db)
            else:
                await self.banco_repository.disminuir_saldo(venta.banco_id, venta.total, session=db)

            await self.detalle_utilidad_repository.delete_by_venta(venta_id, session=db)
            await self.utilidad_repository.delete_by_venta(venta_id, session=db)
            await self.detalle_repository.delete_by_venta(venta_id, session=db)
            await self.venta_repository.delete_venta(venta_id, session=db)