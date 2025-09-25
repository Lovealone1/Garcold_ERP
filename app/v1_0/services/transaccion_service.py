from typing import Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.v1_0.entities import TransaccionDTO, TransaccionListDTO, TransaccionPageDTO, TransaccionResponseDTO
from app.v1_0.models import Transaccion
from app.v1_0.repositories import (
    TransaccionRepository,
    TipoTransaccionRepository,
    BancoRepository,
)
from math import ceil

PAGE_SIZE = 10

class TransaccionService:
    def __init__(
        self,
        transaccion_repository: TransaccionRepository,
        tipo_transaccion_repository: TipoTransaccionRepository,
        banco_repository: BancoRepository,
    ):
        self.trans_repo = transaccion_repository
        self.tipo_repo = tipo_transaccion_repository
        self.banco_repo = banco_repository

    async def insertar_transaccion(
        self,
        transaccion_dto: TransaccionDTO,
        db: AsyncSession
    ) -> Transaccion:
        return await self.trans_repo.create_transaccion(transaccion_dto, session=db)

    async def crear_transaccion(
        self,
        banco_id: int,
        tipo_id: int,
        monto: float,
        descripcion: Optional[str],
        db: AsyncSession
    ) -> TransaccionListDTO:
        if monto <= 0:
            raise HTTPException(400, "El monto debe ser mayor que cero")

        async with db.begin():
            tipo = await self.tipo_repo.get_by_id(tipo_id, session=db)
            if not tipo:
                raise HTTPException(404, f"Tipo de transacción {tipo_id} no encontrado")

            banco = await self.banco_repo.get_by_id(banco_id, session=db)
            if not banco:
                raise HTTPException(404, f"Banco {banco_id} no encontrado")

            nombre = tipo.nombre.lower()
            if nombre not in ("ingreso", "retiro"):
                raise HTTPException(400, f"Tipo '{tipo.nombre}' no soportado")

            if nombre == "retiro":
                if (banco.saldo or 0) < monto:
                    raise HTTPException(400, f"Saldo insuficiente en banco (actual: {banco.saldo:.2f})")
                await self.banco_repo.disminuir_saldo(banco_id, monto, session=db)
            else:
                await self.banco_repo.aumentar_saldo(banco_id, monto, session=db)

            dto = TransaccionDTO(
                banco_id=banco_id,
                tipo_id=tipo_id,
                monto=monto,
                descripcion=descripcion,
            )
            trans = await self.trans_repo.create_transaccion(dto, session=db)

        return TransaccionListDTO(
            id=trans.id,
            banco_id=trans.banco_id,
            monto=trans.monto,
            tipo_id=trans.tipo_id,
            descripcion=getattr(trans, "descripcion", None),
            fecha_creacion=trans.fecha_creacion,
        )

    async def eliminar_transacciones_pago_compra(
        self,
        pago_id: int,
        compra_id: int,
        db: AsyncSession
    ) -> int:
        pago_id = await self.trans_repo.get_transaccion_id_for_pago_compra(pago_id, compra_id, session=db)
        await self.trans_repo.delete_transaccion(pago_id, session=db)
        return pago_id

    async def eliminar_transacciones_pago_venta(
        self,
        pago_id: int,
        venta_id: int,
        db: AsyncSession
    ) -> int:
        pago_id = await self.trans_repo.get_transaccion_id_for_pago_venta(pago_id, venta_id, session=db)
        await self.trans_repo.delete_transaccion(pago_id, session=db)
        return pago_id

    async def eliminar_transacciones_venta(
        self,
        venta_id: int,
        db: AsyncSession
    ) -> int:
        ids = await self.trans_repo.get_ids_for_pago_venta(venta_id, session=db)
        for tid in ids:
            await self.trans_repo.delete_transaccion(tid, session=db)
        return len(ids)

    async def eliminar_transacciones_compra(
        self,
        compra_id: int,
        db: AsyncSession
    ) -> int:
        ids = await self.trans_repo.get_ids_for_pago_compra(compra_id, session=db)
        for tid in ids:
            await self.trans_repo.delete_transaccion(tid, session=db)
        return len(ids)

    async def eliminar_transacciones_gasto(
        self,
        gasto_id: int,
        db: AsyncSession
    ) -> int:
        ids = await self.trans_repo.get_ids_for_gasto(gasto_id, session=db)
        for tid in ids:
            await self.trans_repo.delete_transaccion(tid, session=db)
        return len(ids)

    async def eliminar_transaccion_manual(
        self,
        transaccion_id: int,
        db: AsyncSession
    ) -> bool:
        async with db.begin():
            trans = await self.trans_repo.get_by_id(transaccion_id, session=db)
            if not trans:
                return False

            tipo = await self.tipo_repo.get_by_id(trans.tipo_id, session=db)
            if not tipo:
                raise HTTPException(404, f"Tipo de transacción {trans.tipo_id} no encontrado")

            banco = await self.banco_repo.get_by_id(trans.banco_id, session=db)
            if not banco:
                raise HTTPException(404, f"Banco {trans.banco_id} no encontrado")

            nombre = tipo.nombre.lower()
            if nombre == "ingreso":
                if (banco.saldo or 0) < trans.monto:
                    raise HTTPException(400, f"Saldo insuficiente en banco para revertir ingreso ({banco.saldo:.2f})")
                await self.banco_repo.disminuir_saldo(banco.id, trans.monto, session=db)
            elif nombre == "retiro":
                await self.banco_repo.aumentar_saldo(banco.id, trans.monto, session=db)

            await self.trans_repo.delete(trans, session=db)
        return True

    async def listar_transacciones(self, page: int, db: AsyncSession) -> TransaccionPageDTO:
        offset = (page - 1) * PAGE_SIZE
        async with db.begin():
            items, total = await self.trans_repo.list_paginated(
                offset=offset, limit=PAGE_SIZE, session=db
            )

            tipo_cache: dict[int, str] = {}
            result_items: list[TransaccionResponseDTO] = []

            for t in items:
                if t.tipo_id not in tipo_cache:
                    tipo = await self.tipo_repo.get_by_id(t.tipo_id, session=db)
                    tipo_cache[t.tipo_id] = tipo.nombre if tipo else "Desconocido"

                result_items.append(
                    TransaccionResponseDTO(
                        id=t.id,
                        banco_id=t.banco_id,
                        monto=t.monto,
                        tipo_str=tipo_cache[t.tipo_id],
                        descripcion=getattr(t, "descripcion", None),
                        fecha_creacion=t.fecha_creacion,
                    )
                )

        total = int(total or 0)
        total_pages = max(1, ceil(total / PAGE_SIZE)) if total else 1

        return TransaccionPageDTO(
            items=result_items,
            page=page,
            page_size=PAGE_SIZE,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )
