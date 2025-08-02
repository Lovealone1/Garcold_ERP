from typing import Optional, List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime 

from app.v1_0.entities import TransaccionDTO
from app.v1_0.models import Transaccion
from app.v1_0.repositories import (
    TransaccionRepository,
    TipoTransaccionRepository,
    BancoRepository,
)
from app.v1_0.schemas.transaccion_schema import TransaccionResponseDTO

PAGE_SIZE = 10

class TransaccionService:
    """
    Servicio para gestionar el libro mayor de transacciones.

    - registrar_transaccion(): graba un asiento contable sin tocar saldos bancarios.
    - crear_transaccion(): graba el asiento y ajusta el saldo del banco.
    """

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
        """
        Graba una transacción en el libro mayor sin afectar saldos de banco.

        Args:
            transaccion_dto: DTO con banco_id, tipo_id, monto y descripción opcional.
            db:              Sesión asíncrona de SQLAlchemy.

        Returns:
            Transaccion: La entidad Transaccion recién persistida.
        """
        return await self.trans_repo.create_transaccion(transaccion_dto, session=db)

    async def crear_transaccion(
        self,
        banco_id: int,
        tipo_id: int,
        monto: float,
        descripcion: Optional[str],
        db: AsyncSession
    ) -> TransaccionResponseDTO:
        """
        Persiste una transacción y ajusta el saldo del banco según el tipo:

          - Ingreso: aumenta saldo
          - Retiro : disminuye saldo (verifica fondos)

        Args:
            banco_id:     ID del banco.
            tipo_id:      ID del tipo de transacción.
            monto:        Monto positivo.
            descripcion:  Texto libre que describe la transacción.
            db:           Sesión asíncrona.

        Raises:
            HTTPException 400: monto inválido, tipo no soportado o fondos insuficientes.
            HTTPException 404: banco o tipo no encontrados.

        Returns:
            TransaccionResponseDTO: DTO con los datos de la transacción creada.
        """
        if monto <= 0:
            raise HTTPException(400, "El monto debe ser mayor que cero")

        async with db.begin():
            tipo = await self.tipo_repo.get_by_id(tipo_id, session=db)
            if not tipo:
                raise HTTPException(404, f"Tipo de transacción {tipo_id} no encontrado")

            nombre = tipo.nombre.lower()
            if nombre not in ("ingreso", "retiro"):
                raise HTTPException(400, f"Tipo '{tipo.nombre}' no soportado (solo Ingreso o Retiro)")

            banco = await self.banco_repo.get_by_id(banco_id, session=db)
            if not banco:
                raise HTTPException(404, f"Banco {banco_id} no encontrado")

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

        return TransaccionResponseDTO(
            id=trans.id,
            banco=banco.nombre,
            tipo=tipo.nombre,
            monto=trans.monto,
            descripcion=trans.descripcion,
            fecha_creacion=trans.fecha_creacion
        )
    
    async def eliminar_transacciones_pago_compra(
            self,
            pago_id: int,
            compra_id: int,
            db: AsyncSession
        ) -> int:
            """
            Borra todas las transacciones automáticas de abonos de compra
            (descripciones "<pago_id> Abono compra {compra_id}")
            y retorna cuántas se eliminaron.
            """
            pago_id = await self.trans_repo.get_transaccion_id_for_pago_compra(pago_id ,compra_id, session=db)

 
            await self.trans_repo.delete_transaccion(pago_id, session=db)

            return pago_id
    
    async def eliminar_transacciones_pago_venta(
            self,
            pago_id: int,
            venta_id: int,
            db: AsyncSession
        ) -> int:
            """
            Borra todas las transacciones automáticas de abonos de venta
            (descripciones "<pago_id> Abono venta {venta_id}")
            y retorna cuántas se eliminaron.
            """
            pago_id = await self.trans_repo.get_transaccion_id_for_pago_venta(pago_id ,venta_id, session=db)

 
            await self.trans_repo.delete_transaccion(pago_id, session=db)

            return pago_id
    
    async def eliminar_transacciones_venta(
        self,
        venta_id: int,
        db: AsyncSession
    ) -> int:
        """
        Borra todas las transacciones automáticas de pagos de venta
        y retorna cuántas se eliminaron.
        """
        ids = await self.trans_repo.get_ids_for_pago_venta(venta_id, session=db)
        for tid in ids:
            await self.trans_repo.delete_transaccion(tid, session=db)
        return len(ids)

    async def eliminar_transacciones_compra(
            self,
            compra_id: int,
            db: AsyncSession
        ) -> int:
            """
            Borra todas las transacciones automáticas de pagos de compra
            y retorna cuántas se eliminaron.
            """
            ids = await self.trans_repo.get_ids_for_pago_compra(compra_id, session=db)
            for tid in ids:
                await self.trans_repo.delete_transaccion(tid, session=db)
            return len(ids)
    
    async def eliminar_transacciones_gasto(
        self,
        gasto_id: int,
        db: AsyncSession
    ) -> int:
        """
        Borra todas las transacciones automáticas registradas para un gasto
        (basadas en la descripción "Gasto ...") y devuelve cuántas se eliminaron.

        Args:
            gasto_id (int): ID del gasto cuyas transacciones queremos eliminar.
            db (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            int: Número de transacciones eliminadas.
        """

        ids = await self.trans_repo.get_ids_for_gasto(gasto_id, session=db)

        for tid in ids:
            await self.trans_repo.delete_transaccion(tid, session=db)

        return len(ids)
    
    async def eliminar_transaccion_manual(
        self,
        transaccion_id: int,
        db: AsyncSession
    ) -> bool:
        """
        Elimina una transacción manual (ingreso/retiro) y revierte el ajuste
        de saldo en el banco correspondiente.

        Args:
            transaccion_id: ID de la transacción a eliminar.
            db:             Sesión asíncrona de SQLAlchemy.

        Returns:
            bool: True si existía y fue borrada, False si no se encontró.

        Raises:
            HTTPException 404: Si banco o tipo no existen.
            HTTPException 400: Si el banco no tiene saldo suficiente para revertir un ingreso.
        """
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
                    raise HTTPException(
                        400,
                        f"Saldo insuficiente en banco para revertir ingreso ({banco.saldo:.2f})"
                    )
                await self.banco_repo.disminuir_saldo(banco.id, trans.monto, session=db)
            elif nombre == "retiro":
                await self.banco_repo.aumentar_saldo(banco.id, trans.monto, session=db)
            else:
                pass

            await self.trans_repo.delete(trans, session=db)

        return True

    async def listar_transacciones(
        self,
        page: int,
        session: AsyncSession
    ) -> List[TransaccionResponseDTO]:
        """
        Lista todas las transacciones, 10 por página.
        """
        offset = (page - 1) * PAGE_SIZE
        transs = await self.trans_repo.list_paginated(offset, PAGE_SIZE, session)
        return await self._to_dtos(transs, session)

    async def listar_por_banco(
        self,
        banco_id: int,
        page: int,
        session: AsyncSession
    ) -> List[TransaccionResponseDTO]:
        """
        Lista transacciones de un banco, 10 por página.
        """
        offset = (page - 1) * PAGE_SIZE
        transs = await self.trans_repo.list_by_banco_paginated(
            banco_id, offset, PAGE_SIZE, session
        )
        return await self._to_dtos(transs, session)

    async def listar_por_tipo(
        self,
        tipo_id: int,
        page: int,
        session: AsyncSession
    ) -> List[TransaccionResponseDTO]:
        """
        Lista transacciones de un tipo, 10 por página.
        """
        offset = (page - 1) * PAGE_SIZE
        transs = await self.trans_repo.list_by_tipo_paginated(
            tipo_id, offset, PAGE_SIZE, session
        )
        return await self._to_dtos(transs, session)

    async def listar_por_rango(
        self,
        fecha_inicio: datetime,
        fecha_fin: datetime,
        page: int,
        session: AsyncSession
    ) -> List[TransaccionResponseDTO]:
        """
        Lista transacciones entre dos fechas, 10 por página.
        """
        if fecha_fin < fecha_inicio:
            raise HTTPException(400, "fecha_fin debe ser >= fecha_inicio")

        offset = (page - 1) * PAGE_SIZE
        transs = await self.trans_repo.list_by_rango_paginated(
            fecha_inicio, fecha_fin, offset, PAGE_SIZE, session
        )
        return await self._to_dtos(transs, session)

    # ——— helper para convertir a DTO ———

    async def _to_dtos(
        self,
        transacciones: List[Transaccion],
        session: AsyncSession
    ) -> List[TransaccionResponseDTO]:
        """
        Convierte entidades en DTOs incluyendo nombres de banco y tipo.
        """
        dtos: List[TransaccionResponseDTO] = []
        for t in transacciones:
            banco = await self.banco_repo.get_by_id(t.banco_id, session=session)
            tipo  = await self.tipo_repo.get_by_id(t.tipo_id, session=session)
            dtos.append(
                TransaccionResponseDTO(
                    id=t.id,
                    banco=banco.nombre if banco else "Desconocido",
                    tipo=tipo.nombre   if tipo  else "Desconocido",
                    monto=t.monto,
                    descripcion=t.descripcion,
                    fecha_creacion=t.fecha_creacion
                )
            )
        return dtos