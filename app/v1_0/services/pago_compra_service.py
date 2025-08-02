# app/v1_0/services/pago_compra_service.py

from datetime import datetime
from typing import List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1_0.entities import DetallePagoCompraDTO, TransaccionDTO
from app.v1_0.schemas.pago_venta_schema import PagoResponseDTO
from app.v1_0.repositories import (
    CompraRepository,
    EstadoRepository,
    DetallePagoCompraRepository,
    BancoRepository,
)
from app.v1_0.services.transaccion_service import TransaccionService

class PagoCompraService:
    """
    Servicio para gestionar pagos sobre compras a crédito.
    """
    def __init__(
        self,
        compra_repository: CompraRepository,
        estado_repository: EstadoRepository,
        pago_compra_repository: DetallePagoCompraRepository,
        banco_repository: BancoRepository,
        transaccion_service: TransaccionService
    ):
        self.compra_repo = compra_repository
        self.estado_repo = estado_repository
        self.pago_compra_repo = pago_compra_repository
        self.banco_repo = banco_repository
        self.transaccion_service = transaccion_service

    async def crear_pago_compra(
        self,
        compra_id: int,
        banco_id: int,
        monto: float,
        db: AsyncSession
    ) -> PagoResponseDTO:
        """
        Registra un pago sobre una compra a crédito.

        Descuenta el monto del saldo pendiente de la compra y lo resta del banco.
        Si tras el pago el saldo de la compra queda en cero, actualiza su estado a "compra cancelada".

        Args:
            compra_id (int): ID de la compra a la que se aplica el pago.
            banco_id (int): ID del banco que recibe el pago.
            monto (float): Monto que se va a abonar.
            db (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            PagoResponseDTO: DTO con los datos del pago y estado actualizado de la compra.

        Raises:
            HTTPException 404: Si la compra o el banco no existen.
            HTTPException 400: Si la compra no está a crédito, no tiene saldo pendiente,
                               el monto es inválido/excede el saldo de la compra,
                               o saldo insuficiente en el banco.
        """
        async with db.begin():
            compra = await self.compra_repo.get_by_id(compra_id, session=db)
            banco = await self.banco_repo.get_by_id(banco_id, session=db)
            if not compra:
                raise HTTPException(404, "Compra no encontrada")

            estado = await self.estado_repo.get_by_id(compra.estado_id, session=db)
            if not estado or estado.nombre.lower() != "compra credito":
                raise HTTPException(400, "Solo se pueden pagar compras a crédito")

            if compra.saldo <= 0:
                raise HTTPException(400, "Esta compra ya no tiene saldo pendiente")

            if monto <= 0 or monto > compra.saldo:
                raise HTTPException(400, "Monto inválido o superior al saldo pendiente")
            if banco.saldo < monto:
                raise HTTPException(400, f"Saldo insuficiente en el banco ({banco.saldo:.2f})")

            pago_dto = DetallePagoCompraDTO(
                compra_id=compra_id,
                banco_id=banco_id,
                monto=monto,
                fecha_creacion=datetime.now()
            )
            pago = await self.pago_compra_repo.create_pago(pago_dto, session=db)

            nuevo_saldo = compra.saldo - monto
            await self.compra_repo.update_compra(
                compra_id,
                {"saldo": nuevo_saldo},
                session=db
            )

            if nuevo_saldo == 0:
                estado_cancelada = await self.estado_repo.get_by_nombre(
                    "compra cancelada",
                    session=db
                )
                if estado_cancelada:
                    await self.compra_repo.update_compra(
                        compra_id,
                        {"estado_id": estado_cancelada.id},
                        session=db
                    )

            await self.banco_repo.disminuir_saldo(
                banco_id, monto, session=db
            )
            await self.transaccion_service.insertar_transaccion(
                TransaccionDTO(
                    banco_id=banco_id,
                    monto=monto,
                    tipo_id=3,
                    descripcion=f"{pago.id} Abono compra {compra_id}"
                ),
                db=db
            )

        return PagoResponseDTO(
            id=pago.id,
            venta_id=compra_id,
            banco=banco.nombre if banco else "Desconocido",
            saldo_restante=compra.saldo,
            monto_abonado=pago.monto,
            fecha_creacion=pago.fecha_creacion
        )

    async def listar_pagos_compra(
        self,
        compra_id: int,
        db: AsyncSession
    ) -> List[PagoResponseDTO]:
        """
        Obtiene todos los pagos realizados sobre una compra.

        Args:
            compra_id (int): ID de la compra cuyos pagos se listan.
            db (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            List[PagoResponseDTO]: Lista de DTOs con la información de cada pago.
        """
        pagos = await self.pago_compra_repo.list_by_compra(compra_id, session=db)
        if not pagos:
            return []

        compra = await self.compra_repo.get_by_id(compra_id, session=db)
        saldo = compra.saldo if compra else 0.0

        result: List[PagoResponseDTO] = []
        for pago in pagos:
            banco = await self.banco_repo.get_by_id(pago.banco_id, session=db)
            result.append(PagoResponseDTO(
                id=pago.id,
                venta_id=compra_id,
                banco=banco.nombre if banco else "Desconocido",
                saldo_restante=saldo,
                monto_abonado=pago.monto,
                fecha_creacion=pago.fecha_creacion
            ))
        return result

    async def eliminar_pago_compra(
        self,
        pago_id: int,
        db: AsyncSession
    ) -> bool:
        """
        Elimina un pago de compra.

        Si la compra estaba en "compra cancelada", la cambia a "compra credito",
        suma el monto eliminado al saldo pendiente de la compra
        y lo añade de nuevo al banco.

        Args:
            pago_id (int): ID del pago a eliminar.
            db (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            bool: True si el pago existía y se eliminó; False si no se encontró.

        Raises:
            HTTPException 404: Si la compra asociada no existe.
        """
        async with db.begin():
            pago = await self.pago_compra_repo.get_by_id(pago_id, session=db)
            if not pago:
                return False

            compra = await self.compra_repo.get_by_id(pago.compra_id, session=db)
            if not compra:
                raise HTTPException(404, "Compra asociada no encontrada")

            estado_actual = await self.estado_repo.get_by_id(compra.estado_id, session=db)
            if estado_actual and estado_actual.nombre.lower() == "compra cancelada":
                estado_credito = await self.estado_repo.get_by_nombre("compra credito", session=db)
                if estado_credito:
                    await self.compra_repo.update_compra(
                        compra.id,
                        {"estado_id": estado_credito.id},
                        session=db
                    )

            nuevo_saldo = (compra.saldo or 0) + pago.monto
            await self.compra_repo.update_compra(
                compra.id,
                {"saldo": nuevo_saldo},
                session=db
            )

            await self.banco_repo.aumentar_saldo(
                pago.banco_id,
                pago.monto,
                session=db
            )

            await self.pago_compra_repo.delete_pago(pago_id, session=db)
            await self.transaccion_service.eliminar_transacciones_pago_compra(pago_id,compra.id, db=db)
        return True
