from datetime import datetime
from typing import List
from fastapi import HTTPException

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
        detalles = []
        for item in carrito:
            total = item.cantidad * item.precio
            detalle = DetalleCompraDTO(
                producto_id=item.producto_id,
                cantidad=item.cantidad,
                precio=item.precio,
                total=total,
                compra_id=0
            )
            detalles.append(detalle)
        return detalles

    async def registrar_compra(
        self,
        proveedor_id: int,
        banco_id: int,
        estado_id: int,
        detalles: List[DetalleCompraDTO]
    ) -> Compra:
        total_compra = 0.0

        for detalle in detalles:
            producto = await self.producto_repository.get_by_id(detalle.producto_id)
            if not producto:
                raise HTTPException(status_code=404, detail=f"Producto {detalle.producto_id} no encontrado")
            total_compra += detalle.total

        estado = await self.estado_repository.get_by_id(estado_id)
        es_credito = estado and estado.nombre.lower() == "compra credito"

        saldo = total_compra if es_credito else 0.0
        compra_dto = CompraDTO(
            proveedor_id=proveedor_id,
            banco_id=banco_id,
            estado_id=estado_id,
            total=total_compra,
            saldo=saldo,
            fecha=datetime.now()
        )

        try:
            compra = await self.compra_repository.create_compra(compra_dto)

            detalles_con_id = [
                DetalleCompraDTO(
                    producto_id=d.producto_id,
                    cantidad=d.cantidad,
                    precio=d.precio,
                    total=d.total,
                    compra_id=compra.id
                ) for d in detalles
            ]
            await self.detalle_repository.bulk_insert_detalles(detalles_con_id)

            for d in detalles:
                await self.producto_repository.aumentar_cantidad(d.producto_id, d.cantidad)

            if not es_credito:
                banco = await self.banco_repository.get_by_id(banco_id)
                if banco:
                    nuevo_saldo = (banco.saldo or 0) - total_compra
                    await self.banco_repository.update_saldo(banco_id, nuevo_saldo)

            return compra
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al registrar compra: {str(e)}")

    async def obtener_compra(self, compra_id: int) -> CompraResponse:
        compra = await self.compra_repository.get_by_id(compra_id)
        if not compra:
            raise HTTPException(status_code=404, detail="Compra no encontrada")

        proveedor = await self.proveedor_repository.get_by_id(compra.proveedor_id)
        banco = await self.banco_repository.get_by_id(compra.banco_id)
        estado = await self.estado_repository.get_by_id(compra.estado_id)

        return CompraResponse(
            id=compra.id,
            proveedor=proveedor.nombre if proveedor else "Desconocido",
            banco=banco.nombre if banco else "Desconocido",
            estado=estado.nombre if estado else "Desconocido",
            total=compra.total,
            saldo=compra.saldo,
            fecha=compra.fecha
        )

    async def eliminar_compra(self, compra_id: int) -> bool:
        compra = await self.compra_repository.get_by_id(compra_id)
        if not compra:
            raise HTTPException(status_code=404, detail="Compra no encontrada")

        detalles = await self.detalle_repository.get_by_compra_id(compra_id)

        for d in detalles:
            await self.producto_repository.disminuir_cantidad(d.producto_id, d.cantidad)

        estado = await self.estado_repository.get_by_id(compra.estado_id)
        es_credito = estado and estado.nombre.lower() == "compra credito"

        if not es_credito:
            await self.banco_repository._aumentar_saldo(compra.banco_id, compra.total)

        await self.detalle_repository.delete_by_compra(compra_id)
        return await self.compra_repository.delete_compra(compra_id)
