from datetime import datetime
from typing import List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1_0.entities import DetallePagoVentaDTO, TransaccionDTO, PagoResponseDTO
from app.v1_0.repositories import (
    VentaRepository,
    EstadoRepository,
    DetallePagoVentaRepository,
    BancoRepository
)
from app.v1_0.services.transaccion_service import TransaccionService

class PagoVentaService:
    """
    Servicio para gestionar pagos sobre compras y ventas a crédito.
    """

    def __init__(
        self,
        venta_repository: VentaRepository,
        estado_repository: EstadoRepository,
        pago_venta_repository: DetallePagoVentaRepository,
        banco_repository: BancoRepository,
        transaccion_service: TransaccionService
    ):
        self.venta_repo = venta_repository
        self.estado_repo = estado_repository
        self.pago_venta_repo = pago_venta_repository
        self.banco_repo = banco_repository
        self.transaccion_service = transaccion_service

    async def crear_pago_venta(
            self,
            venta_id: int,
            banco_id: int,
            monto: float,
            db: AsyncSession
        ) -> PagoResponseDTO:
            """Registra un pago sobre una venta a crédito.

            Descuenta el monto del saldo pendiente de la venta y lo añade al saldo del banco.
            Si tras el pago el saldo de la venta queda en cero, actualiza su estado a “venta cancelada”.

            Args:
                venta_id (int): ID de la venta a la que se aplica el pago.
                banco_id (int): ID del banco que recibe el pago.
                monto (float): Monto que se va a abonar.
                db (AsyncSession): Sesión asíncrona de SQLAlchemy.

            Returns:
                PagoResponseDTO: DTO con los datos del pago y estado actualizado de la venta.

            Raises:
                HTTPException 404: Si la venta o el banco no existen.
                HTTPException 400: Si la venta no está a crédito, no tiene saldo pendiente,
                                o el monto es inválido/excede el saldo.
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
                await self.transaccion_service.insertar_transaccion(
                    TransaccionDTO(
                        banco_id=banco_id,
                        monto=monto,
                        tipo_id=3,
                        descripcion=f"{pago.id} Abono venta {venta_id}"
                    ),
                    db=db
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
        """Obtiene todos los pagos realizados sobre una venta.

        Args:
            venta_id (int): ID de la venta cuyo historial de pagos se consulta.
            db (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            List[PagoResponseDTO]: Lista de DTOs con la información de cada pago.
        """
        pagos = await self.pago_venta_repo.list_by_venta(venta_id, session=db)
        if not pagos:
            return []

        venta = await self.venta_repo.get_by_id(venta_id, session=db)
        saldo_restante = venta.saldo_restante if venta else 0.0

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
        """Elimina un pago de venta.

        Si la venta estaba en “venta cancelada”, la cambia a “venta credito”,
        restaura el saldo pendiente y descuenta del banco el monto del pago eliminado.

        Args:
            pago_id (int): ID del pago a eliminar.
            db (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            bool: True si el pago existía y se eliminó; False en caso contrario.

        Raises:
            HTTPException 404: Si la venta asociada no existe.
        """
        async with db.begin():
            pago = await self.pago_venta_repo.get_by_id(pago_id, session=db)
            if not pago:
                return False

            venta = await self.venta_repo.get_by_id(pago.venta_id, session=db)
            if not venta:
                raise HTTPException(404, "Venta asociada no encontrada")

            estado_actual = await self.estado_repo.get_by_id(venta.estado_id, session=db)
            if estado_actual and estado_actual.nombre.lower() == "venta cancelada":
                estado_credito = await self.estado_repo.get_by_nombre("venta credito", session=db)
                if estado_credito:
                    await self.venta_repo.update_venta(
                        venta.id,
                        {"estado_id": estado_credito.id},
                        session=db
                    )

            nuevo_saldo = (venta.saldo_restante or 0) + pago.monto
            await self.venta_repo.update_venta(
                venta.id,
                {"saldo_restante": nuevo_saldo},
                session=db
            )

            await self.banco_repo.disminuir_saldo(
                pago.banco_id,
                pago.monto,
                session=db
            )

            await self.pago_venta_repo.delete_pago(pago_id, session=db)
            await self.transaccion_service.eliminar_transacciones_pago_venta(pago_id,venta.id, db=db)
        return True


