from datetime import datetime
from typing import List
from fastapi import HTTPException

from app.v1_0.entities import VentaDTO, DetalleVentaDTO, DetalleUtilidadDTO, UtilidadDTO
from app.v1_0.models import Venta
from app.v1_0.repositories import (
    VentaRepository,
    DetalleVentaRepository,
    ProductoRepository,
    ClienteRepository,
    EstadoRepository,
    DetalleUtilidadRepository,
    UtilidadRepository
)


class VentaService:
    def __init__(
        self,
        venta_repository: VentaRepository,
        detalle_repository: DetalleVentaRepository,
        producto_repository: ProductoRepository,
        cliente_repository: ClienteRepository,
        estado_repository: EstadoRepository,
        detalle_utilidad_repository: DetalleUtilidadRepository,
        utilidad_repository: UtilidadRepository
    ):
        self.venta_repository = venta_repository
        self.detalle_repository = detalle_repository
        self.producto_repository = producto_repository
        self.cliente_repository = cliente_repository
        self.estado_repository = estado_repository
        self.detalle_utilidad_repository = detalle_utilidad_repository
        self.utilidad_repository = utilidad_repository

    def agregar_detalle_venta(self, carrito: List[dict]) -> List[DetalleVentaDTO]:
        """
        Construye objetos DetalleVentaDTO a partir de datos del frontend o lógica de aplicación.

        Args:
            carrito (List[dict]): Lista de ítems con producto_id, cantidad y precio_producto.

        Returns:
            List[DetalleVentaDTO]: Detalles de la venta sin persistencia.
        """
        detalles = []
        for item in carrito:
            total = item.cantidad * item.precio_producto
            detalle = DetalleVentaDTO(
                producto_id=item.producto_id,
                cantidad=item.cantidad,
                precio_producto=item.precio_producto,
                total=total,
                venta_id=0
            )
            detalles.append(detalle)
        return detalles

    async def finalizar_venta(
        self,
        cliente_id: int,
        banco_id: int,
        estado_id: int,
        detalles: List[DetalleVentaDTO]
    ) -> Venta:
        total_venta = 0.0

        for detalle in detalles:
            producto = await self.producto_repository.get_by_id(detalle.producto_id)
            if not producto:
                raise HTTPException(status_code=404, detail=f"Producto {detalle.producto_id} no encontrado")
            if (producto.cantidad or 0) < detalle.cantidad:
                raise HTTPException(status_code=400, detail=f"Stock insuficiente para producto {producto.referencia}")
            total_venta += detalle.total

        venta_dto = VentaDTO(
            cliente_id=cliente_id,
            banco_id=banco_id,
            total=total_venta,
            estado_id=estado_id,
            saldo_restante=total_venta,
            fecha=datetime.now()
        )
        venta = await self.venta_repository.create_venta(venta_dto)

        detalles_con_id = [
            DetalleVentaDTO(
                producto_id=d.producto_id,
                cantidad=d.cantidad,
                precio_producto=d.precio_producto,
                total=d.total,
                venta_id=venta.id
            ) for d in detalles
        ]
        await self.detalle_repository.bulk_insert_detalles(detalles_con_id)

        for d in detalles:
            await self.producto_repository.disminuir_cantidad(d.producto_id, d.cantidad)

        estado = await self.estado_repository.get_by_id(estado_id)
        if estado and estado.nombre.lower() == "venta credito":
            cliente = await self.cliente_repository.get_by_id(cliente_id)
            if cliente:
                nuevo_saldo = (cliente.saldo or 0) + total_venta
                await self.cliente_repository.update_saldo(cliente_id, nuevo_saldo)

        detalles_utilidad = await self.agregar_detalle_utilidad(detalles_con_id)
        await self.registrar_utilidad(venta.id, detalles_utilidad)

        return venta

    async def agregar_detalle_utilidad(self, detalles: List[DetalleVentaDTO]) -> List[DetalleUtilidadDTO]:
        detalle_utilidades = []
        for d in detalles:
            producto = await self.producto_repository.get_by_id(d.producto_id)
            if not producto:
                raise HTTPException(status_code=404, detail=f"Producto {d.producto_id} no encontrado")
            utilidad_unitaria = d.precio_producto - producto.precio_compra
            total_utilidad = utilidad_unitaria * d.cantidad

            detalle_utilidad = DetalleUtilidadDTO(
                venta_id=d.venta_id,
                producto_id=d.producto_id,
                cantidad=d.cantidad,
                precio_compra=producto.precio_compra,
                precio_venta=d.precio_producto,
                total_utilidad=total_utilidad
            )
            detalle_utilidades.append(detalle_utilidad)
        return detalle_utilidades

    async def registrar_utilidad(self, venta_id: int, detalles_utilidad: List[DetalleUtilidadDTO]):
        utilidad_total = sum([d.total_utilidad for d in detalles_utilidad])
        await self.detalle_utilidad_repository.bulk_insert_detalles(detalles_utilidad)

        utilidad_dto = UtilidadDTO(
            venta_id=venta_id,
            utilidad=utilidad_total
        )
        await self.utilidad_repository.create_utilidad(utilidad_dto)

    async def delete_venta(self, venta_id: int) -> bool:
        venta = await self.venta_repository.get_by_id(venta_id)
        if not venta:
            raise HTTPException(status_code=404, detail="Venta no encontrada")
        return await self.venta_repository.delete_venta(venta_id)