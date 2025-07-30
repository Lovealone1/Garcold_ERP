from datetime import datetime
from typing import List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1_0.entities import DetallePagoVentaDTO, DetallePagoCompraDTO
from app.v1_0.models import DetallePagoVenta, DetallePagoCompra
from app.v1_0.schemas.pago_venta_schema import PagoResponseDTO  
from app.v1_0.repositories import (
    VentaRepository,
    CompraRepository,
    EstadoRepository,
    DetallePagoVentaRepository,
    DetallePagoCompraRepository, 
    BancoRepository
)

class PagoVentaService:
    """
    Servicio para gestionar pagos sobre compras y ventas a crédito.
    """

    def __init__(
        self,
        venta_repository: VentaRepository,
        compra_repository: CompraRepository,
        estado_repository: EstadoRepository,
        pago_venta_repository: DetallePagoVentaRepository,
        pago_compra_repository: DetallePagoCompraRepository,
        banco_repository: BancoRepository
    ):
        """
        Inicializa con los repositorios necesarios.
        """
        self.venta_repo = venta_repository
        self.compra_repo = compra_repository
        self.estado_repo = estado_repository
        self.pago_venta_repo = pago_venta_repository
        self.pago_compra_repo = pago_compra_repository
        self.banco_repo = banco_repository
    async def crear_pago_venta(
            self,
            venta_id: int,
            banco_id: int,
            monto: float,
            db: AsyncSession
        ) -> PagoResponseDTO:
            """
            Registra un pago sobre una venta a crédito, decrementando su saldo.
            Si al aplicar el pago el saldo restante queda en 0, cambia el estado
            de la venta a "venta cancelada".
            """
            async with db.begin():
                venta = await self.venta_repo.get_by_id(venta_id, session=db)
                if not venta:
                    raise HTTPException(404, "Venta no encontrada")

                estado = await self.estado_repo.get_by_id(venta.estado_id, session=db)
                if not estado or estado.nombre.lower() != "venta credito":
                    raise HTTPException(400, "Solo se pueden pagar ventas a crédito")

                if venta.saldo_restante <= 0:
                    raise HTTPException(400, "Esta venta ya no tiene saldo pendiente")

                if monto <= 0 or monto > venta.saldo_restante:
                    raise HTTPException(400, "Monto inválido o superior al saldo pendiente")

                pago_dto = DetallePagoVentaDTO(
                    venta_id=venta_id,
                    banco_id=banco_id,
                    monto=monto,
                    fecha_creacion=datetime.now()
                )
                pago = await self.pago_venta_repo.create_pago(pago_dto, session=db)

                nuevo_saldo = venta.saldo_restante - monto
                await self.venta_repo.update_venta(
                    venta_id,
                    {"saldo_restante": nuevo_saldo},
                    session=db
                )

                if nuevo_saldo == 0:
                    estado_cancelada = await self.estado_repo.get_by_nombre(
                        "venta cancelada",
                        session=db
                    )
                    if estado_cancelada:
                        await self.venta_repo.update_venta(
                            venta_id,
                            {"estado_id": estado_cancelada.id},
                            session=db
                        )

                await self.banco_repo.aumentar_saldo(
                    banco_id, monto, session=db
                )
                banco = await self.banco_repo.get_by_id(banco_id, session=db)

            return PagoResponseDTO(
                id=pago.id,
                venta_id=venta_id,
                banco=banco.nombre if banco else "Desconocido",
                saldo_restante=venta.saldo_restante,
                monto_abonado=pago.monto,
                fecha_creacion=pago.fecha_creacion
            )

    async def listar_pagos_venta(
        self,
        venta_id: int,
        db: AsyncSession
    ) -> List[PagoResponseDTO]:
        """
        Devuelve todos los pagos de una venta, serializados como PagoResponseDTO.
        """
        # 1) Recuperar todos los pagos
        pagos = await self.pago_venta_repo.list_by_venta(venta_id, session=db)
        if not pagos:
            return []

        # 2) Recuperar datos comunes de la venta (total)
        venta = await self.venta_repo.get_by_id(venta_id, session=db)
        saldo_restante = venta.saldo_restante if venta else 0.0

        # 3) Para cada pago, buscar el nombre de banco y construir el DTO
        result: List[PagoResponseDTO] = []
        for pago in pagos:
            banco = await self.banco_repo.get_by_id(pago.banco_id, session=db)
            result.append(PagoResponseDTO(
                id=pago.id,
                venta_id=pago.venta_id,
                banco=banco.nombre if banco else "Desconocido",
                saldo_restante=saldo_restante,
                monto_abonado=pago.monto,
                fecha_creacion=pago.fecha_creacion
            ))

        return result

    async def eliminar_pago_venta(
        self,
        pago_id: int,
        db: AsyncSession
    ) -> bool:
        """
        Elimina un pago de venta. Si la venta estaba en 'venta cancelada',
        la pasa de nuevo a 'venta credito', devuelve el monto al saldo pendiente
        y descuenta ese mismo monto del banco.
        """
        async with db.begin():
            # 1) Recuperar el registro de pago
            pago = await self.pago_venta_repo.get_by_id(pago_id, session=db)
            if not pago:
                return False

            # 2) Recuperar la venta asociada
            venta = await self.venta_repo.get_by_id(pago.venta_id, session=db)
            if not venta:
                raise HTTPException(404, "Venta asociada no encontrada")

            # 3) Si la venta estaba saldada ("venta cancelada"), volverla a crédito
            estado_actual = await self.estado_repo.get_by_id(venta.estado_id, session=db)
            if estado_actual and estado_actual.nombre.lower() == "venta cancelada":
                estado_credito = await self.estado_repo.get_by_nombre("venta credito", session=db)
                if estado_credito:
                    await self.venta_repo.update_venta(
                        venta.id,
                        {"estado_id": estado_credito.id},
                        session=db
                    )

            # 4) Revertir el saldo pendiente en la venta
            nuevo_saldo = (venta.saldo_restante or 0) + pago.monto
            await self.venta_repo.update_venta(
                venta.id,
                {"saldo_restante": nuevo_saldo},
                session=db
            )

            # 5) Quitar el monto del banco
            await self.banco_repo.disminuir_saldo(
                pago.banco_id,
                pago.monto,
                session=db
            )

            # 6) Eliminar el pago
            await self.pago_venta_repo.delete_pago(pago_id, session=db)

        return True


