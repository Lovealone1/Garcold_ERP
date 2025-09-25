from datetime import datetime
from typing import List, Dict, Any
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from math import ceil

from app.v1_0.entities import (
    VentaDTO,
    DetalleVentaDTO,
    UtilidadDTO,
    TransaccionDTO,
    DetalleUtilidadDTO,
    VentaListDTO,
    VentasPageDTO,
    DetalleVentaViewDTO
)
from app.v1_0.repositories import (
    VentaRepository,
    DetalleVentaRepository,
    ProductoRepository,
    ClienteRepository,
    EstadoRepository,
    DetalleUtilidadRepository,
    UtilidadRepository,
    BancoRepository,
    DetallePagoVentaRepository,
)
from app.v1_0.services.transaccion_service import TransaccionService
from app.v1_0.schemas.venta_schema import DetalleVentaCreate
PAGE_SIZE = 13


class VentaService:
    def __init__(
        self,
        venta_repository: VentaRepository,
        detalle_repository: DetalleVentaRepository,
        producto_repository: ProductoRepository,
        cliente_repository: ClienteRepository,
        estado_repository: EstadoRepository,
        detalle_utilidad_repository: DetalleUtilidadRepository,
        utilidad_repository: UtilidadRepository,
        banco_repository: BancoRepository,
        pago_venta_repository: DetallePagoVentaRepository,
        transaccion_service: TransaccionService,
    ):
        self.venta_repository = venta_repository
        self.detalle_repository = detalle_repository
        self.producto_repository = producto_repository
        self.cliente_repository = cliente_repository
        self.estado_repository = estado_repository
        self.detalle_utilidad_repository = detalle_utilidad_repository
        self.utilidad_repository = utilidad_repository
        self.banco_repository = banco_repository
        self.pago_venta_repository = pago_venta_repository
        self.transaccion_service = transaccion_service

    async def finalizar_venta(
    self,
    cliente_id: int,
    banco_id: int,
    estado_id: int,
    carrito: List[Dict[str, Any]],
    db: AsyncSession,
    ) -> VentaListDTO:
        """
        Finaliza una venta a partir del carrito JSON del frontend y retorna un VentaListDTO.
        """
        async with db.begin():
            # 1) Leer estado para saber si es crédito/contado
            estado = await self.estado_repository.get_by_id(estado_id, session=db)
            es_credito = bool(estado and estado.nombre.lower() == "venta credito")

            # 2) Crear la venta primero (total y saldo se actualizan luego)
            venta_dto = VentaDTO(
                cliente_id=cliente_id,
                banco_id=banco_id,
                total=0.0,
                estado_id=estado_id,
                saldo_restante=0.0,
                fecha=datetime.now(),
            )
            venta = await self.venta_repository.create_venta(venta_dto, session=db)

            # 3) Construir detalles CON venta_id
            detalles = await self._build_detalles_desde_carrito(
                carrito=carrito, venta_id=venta.id
            )

            # 4) Validar stock y calcular total
            total_venta = 0.0
            for d in detalles:
                producto = await self.producto_repository.get_by_id(d.producto_id, session=db)
                if not producto:
                    raise HTTPException(404, f"Producto {d.producto_id} no encontrado")
                if (producto.cantidad or 0) < d.cantidad:
                    raise HTTPException(400, f"Stock insuficiente para producto {producto.referencia}")
                total_venta += d.total

            # 5) Insertar detalles (pasando DTOs, no dicts)
            rows: list[DetalleVentaCreate] = [
                DetalleVentaCreate(
                    venta_id=venta.id,
                    producto_id=d.producto_id,
                    cantidad=d.cantidad,
                    precio_producto=d.precio_producto,
                )
                for d in detalles
            ]

            await self.detalle_repository.bulk_insert_detalles(rows, session=db)

            # 6) Actualizar totales de la venta ya creada
            nuevo_saldo = total_venta if es_credito else 0.0
            # Si tienes un método específico:
            if hasattr(self.venta_repository, "update_totales"):
                await self.venta_repository.update_totales(
                    venta_id=venta.id,
                    total=total_venta,
                    saldo_restante=nuevo_saldo,
                    session=db,
                )
            else:
                # fallback genérico
                venta.total = total_venta
                venta.saldo_restante = nuevo_saldo
                db.add(venta)

            # 7) Descontar inventario
            for d in detalles:
                await self.producto_repository.disminuir_cantidad(d.producto_id, d.cantidad, session=db)

            # 8) Ajustar saldos / transacción
            if es_credito:
                cliente = await self.cliente_repository.get_by_id(cliente_id, session=db)
                if cliente:
                    nuevo_saldo_cliente = (cliente.saldo or 0) + total_venta
                    await self.cliente_repository.update_saldo(cliente_id, nuevo_saldo_cliente, session=db)
            else:
                banco = await self.banco_repository.get_by_id(banco_id, session=db)
                if banco:
                    nuevo_saldo_banco = (banco.saldo or 0) + total_venta
                    await self.banco_repository.update_saldo(banco_id, nuevo_saldo_banco, session=db)
                    await self.transaccion_service.insertar_transaccion(
                        TransaccionDTO(
                            banco_id=banco_id,
                            monto=total_venta,
                            tipo_id=3,  # Pago venta
                            descripcion=f"Pago venta {venta.id}",
                        ),
                        db=db,
                    )

            # 9) Calcular y registrar utilidades
            detalle_utilidades = await self._calcular_detalle_utilidad(venta.id, detalles, session=db)
            await self.detalle_utilidad_repository.bulk_insert_detalles(detalle_utilidades, session=db)
            utilidad_total = sum(d.total_utilidad for d in detalle_utilidades)
            await self.utilidad_repository.create_utilidad(
                UtilidadDTO(venta_id=venta.id, utilidad=utilidad_total),
                session=db,
            )

            # 10) Resolver nombres para el DTO de salida
            cliente = await self.cliente_repository.get_by_id(cliente_id, session=db)
            banco = await self.banco_repository.get_by_id(banco_id, session=db)

        return VentaListDTO(
            id=venta.id,
            cliente=cliente.nombre if cliente else "Desconocido",
            banco=banco.nombre if banco else "Desconocido",
            estado=estado.nombre if estado else "Desconocido",
            total=total_venta,
            saldo_restante=nuevo_saldo,
            fecha=venta.fecha,
        )

    async def _build_detalles_desde_carrito(
    self,
    carrito: List[Dict[str, Any]],
    venta_id: int,  # <— ahora se exige venta_id
    ) -> List[DetalleVentaDTO]:
        """
        Valida/normaliza el carrito del front y construye DetalleVentaDTOs ya con venta_id.
        """
        detalles: List[DetalleVentaDTO] = []
        for i, raw in enumerate(carrito, start=1):
            try:
                producto_id = int(raw["producto_id"])
                cantidad = int(raw["cantidad"])
                precio = float(raw["precio_producto"])
            except Exception:
                raise HTTPException(400, f"Item #{i} inválido (tipos incorrectos)")

            if cantidad <= 0:
                raise HTTPException(400, f"Item #{i}: cantidad debe ser > 0")
            if precio <= 0:
                raise HTTPException(400, f"Item #{i}: precio_producto debe ser > 0")

            total = cantidad * precio
            detalles.append(
                DetalleVentaDTO(
                    venta_id=venta_id,
                    producto_id=producto_id,
                    cantidad=cantidad,
                    precio_producto=precio,
                    total=total,
                )
            )
        return detalles

    async def _calcular_detalle_utilidad(
        self,
        venta_id: int,
        detalles: List[DetalleVentaDTO],
        session: AsyncSession,
    ) -> List[DetalleUtilidadDTO]:
        """
        Calcula utilidades por línea a partir de los detalles (sin venta_id en DTO),
        y retorna DetalleUtilidadDTO listos para insertar (con venta_id).
        """
        out: List[DetalleUtilidadDTO] = []
        for d in detalles:
            producto = await self.producto_repository.get_by_id(d.producto_id, session=session)
            if not producto:
                raise HTTPException(404, f"Producto {d.producto_id} no encontrado")
            utilidad_unit = d.precio_producto - producto.precio_compra
            total_utilidad = utilidad_unit * d.cantidad
            out.append(
                DetalleUtilidadDTO(
                    venta_id=venta_id,
                    producto_id=d.producto_id,
                    cantidad=d.cantidad,
                    precio_compra=producto.precio_compra,
                    precio_venta=d.precio_producto,
                    total_utilidad=total_utilidad,
                )
            )
        return out

    async def obtener_venta(self, venta_id: int, db: AsyncSession) -> VentaListDTO:
        """
        Obtiene una venta y la devuelve como VentaListDTO.
        """
        venta = await self.venta_repository.get_by_id(venta_id, session=db)
        if not venta:
            raise HTTPException(404, "Venta no encontrada")

        cliente = await self.cliente_repository.get_by_id(venta.cliente_id, session=db)
        banco = await self.banco_repository.get_by_id(venta.banco_id, session=db)
        estado = await self.estado_repository.get_by_id(venta.estado_id, session=db)

        return VentaListDTO(
            id=venta.id,
            cliente=cliente.nombre if cliente else "Desconocido",
            banco=banco.nombre if banco else "Desconocido",
            estado=estado.nombre if estado else "Desconocido",
            total=venta.total,
            saldo_restante=venta.saldo_restante,
            fecha=venta.fecha,
        )

    async def eliminar_venta(self, venta_id: int, db: AsyncSession) -> None:
        async with db.begin():
            venta = await self.venta_repository.get_by_id(venta_id, session=db)
            if not venta:
                raise HTTPException(404, "Venta no encontrada")

            detalles = await self.detalle_repository.get_by_venta_id(venta_id, session=db)
            for d in detalles:
                await self.producto_repository.aumentar_cantidad(d.producto_id, d.cantidad, session=db)

            estado = await self.estado_repository.get_by_id(venta.estado_id, session=db)
            estado_nombre = (estado.nombre or "").lower() if estado else ""
            es_tipo_credito = estado_nombre in ("venta credito", "venta cancelada")
            es_contado = estado_nombre == "venta contado"

            pagos = await self.pago_venta_repository.list_by_venta(venta_id, session=db)

            if es_tipo_credito:
                for pago in pagos:
                    await self.banco_repository.disminuir_saldo(pago.banco_id, pago.monto, session=db)
                cliente = await self.cliente_repository.get_by_id(venta.cliente_id, session=db)
                if cliente:
                    nuevo_saldo = max((cliente.saldo or 0) - venta.total, 0)
                    await self.cliente_repository.update_saldo(cliente.id, nuevo_saldo, session=db)
            elif es_contado:
                await self.banco_repository.disminuir_saldo(venta.banco_id, venta.total, session=db)


            await self.pago_venta_repository.delete_by_venta(venta_id, session=db)
            await self.detalle_utilidad_repository.delete_by_venta(venta_id, session=db)
            await self.utilidad_repository.delete_by_venta(venta_id, session=db)
            await self.detalle_repository.delete_by_venta(venta_id, session=db)
            await self.transaccion_service.eliminar_transacciones_venta(venta_id, db=db)
            await self.venta_repository.delete_venta(venta_id, session=db)

    async def listar_ventas(self, page: int, db: AsyncSession) -> VentasPageDTO:
        """
        Lista ventas paginadas (id asc) con metadatos.
        """
        offset = (page - 1) * PAGE_SIZE
        async with db.begin():
            items_models, total = await self.venta_repository.list_paginated(offset=offset, limit=PAGE_SIZE, session=db)

            items: List[VentaListDTO] = []
            for v in items_models:
                cliente = await self.cliente_repository.get_by_id(v.cliente_id, session=db)
                banco = await self.banco_repository.get_by_id(v.banco_id, session=db)
                estado = await self.estado_repository.get_by_id(v.estado_id, session=db)
                items.append(
                    VentaListDTO(
                        id=v.id,
                        cliente=cliente.nombre if cliente else "Desconocido",
                        banco=banco.nombre if banco else "Desconocido",
                        estado=estado.nombre if estado else "Desconocido",
                        total=v.total,
                        saldo_restante=v.saldo_restante,
                        fecha=v.fecha,
                    )
                )

        total_pages = max(1, ceil(total / PAGE_SIZE)) if total else 1
        return VentasPageDTO(
            items=items,
            page=page,
            page_size=PAGE_SIZE,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )


    async def listar_detalles(self, venta_id: int, db: AsyncSession) -> List[DetalleVentaViewDTO]:
            """
            Devuelve los detalles de una venta listos para visualización:
            producto_referencia, cantidad, precio, total y venta asociada.
            """
            async with db.begin():
                venta = await self.venta_repository.get_by_id(venta_id, session=db)
                if not venta:
                    raise HTTPException(404, "Venta no encontrada")

                detalles = await self.detalle_repository.get_by_venta_id(venta_id, session=db)

                out: List[DetalleVentaViewDTO] = []
                for d in detalles:
                    prod = await self.producto_repository.get_by_id(d.producto_id, session=db)
                    referencia = prod.referencia if prod else "Desconocido"
                    out.append(
                        DetalleVentaViewDTO(
                            venta_id=venta_id,
                            producto_referencia=referencia,
                            cantidad=d.cantidad,
                            precio=d.precio_producto,
                            total=d.total,
                        )
                    )

            return out