from typing import List, Optional
from sqlalchemy import select, desc, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.v1_0.models import Transaccion
from app.v1_0.entities import TransaccionDTO
from app.v1_0.schemas.transaccion_schema import TransaccionResponseDTO
from .base_repository import BaseRepository

PAGE_SIZE = 10

class TransaccionRepository(BaseRepository[Transaccion]):
    """
    Repositorio para operaciones CRUD sobre la entidad Transaccion.
    Cada método recibe explícitamente una AsyncSession.
    """

    def __init__(self):
        super().__init__(Transaccion)

    async def create_transaccion(
        self,
        transaccion_dto: TransaccionDTO,
        session: AsyncSession
    ) -> Transaccion:
        """
        Crea una nueva Transaccion a partir del DTO y hace flush/commit
        para asignar su ID.

        Args:
            transaccion_dto (TransaccionDTO): DTO con los datos de la transacción.
            session (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            Transaccion: La entidad Transaccion recién creada.
        """
        transaccion = Transaccion(**transaccion_dto.model_dump())
        await self.add(transaccion, session)
        return transaccion

    async def list_transacciones(
        self,
        session: AsyncSession,
        limit: int = 10,
        offset: int = 0
    ) -> List[Transaccion]:
        """
        Recupera todas las transacciones paginadas.

        Args:
            session (AsyncSession): Sesión asíncrona de SQLAlchemy.
            limit (int): Número máximo de registros a devolver.
            offset (int): Número de registros a saltar.

        Returns:
            List[Transaccion]: Lista de transacciones.
        """
        stmt = (
            select(Transaccion)
            .order_by(desc(Transaccion.fecha))
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def list_by_tipo(
        self,
        tipo_id: int,
        session: AsyncSession,
        limit: int = 10,
        offset: int = 0
    ) -> List[Transaccion]:
        """
        Recupera transacciones de un tipo específico, paginadas.

        Args:
            tipo_id (int): ID del tipo de transacción.
            session (AsyncSession): Sesión asíncrona de SQLAlchemy.
            limit (int): Número máximo de registros a devolver.
            offset (int): Número de registros a saltar.

        Returns:
            List[Transaccion]: Lista de transacciones filtradas por tipo.
        """
        stmt = (
            select(Transaccion)
            .where(Transaccion.tipo_id == tipo_id)
            .order_by(desc(Transaccion.fecha))
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def delete_transaccion(
        self,
        transaccion_id: int,
        session: AsyncSession
    ) -> bool:
        """
        Elimina una transacción por su ID.

        Args:
            transaccion_id (int): ID de la transacción a eliminar.
            session (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            bool: True si existía y se borró, False en caso contrario.
        """
        transaccion = await self.get_by_id(transaccion_id, session)
        if not transaccion:
            return False
        await self.delete(transaccion, session)
        return True

    async def get_ids_for_pago_compra(
        self,
        compra_id: int,
        session: AsyncSession
    ) -> List[int]:
        """
        Busca todas las transacciones automáticas de pagos de compra (tanto
        'pago compra {compra_id}' como 'abono compra {compra_id}') y devuelve sus IDs.
        """
        # Construimos los dos patrones a buscar
        p1 = f"%pago compra {compra_id}%"
        p2 = f"%abono compra {compra_id}%"

        stmt = select(Transaccion.id).where(
            or_(
                Transaccion.descripcion.ilike(p1),
                Transaccion.descripcion.ilike(p2)
            )
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_ids_for_pago_venta(
        self,
        venta_id: int,
        session: AsyncSession
    ) -> List[int]:
        """
        Busca todas las transacciones cuya descripción contenga 'pago venta {venta_id}'
        y devuelve sus IDs.
        """
        pattern = f"%pago venta {venta_id}%"
        stmt = select(Transaccion.id).where(Transaccion.descripcion.ilike(pattern))
        result = await session.execute(stmt)
        return result.scalars().all()
    
    async def get_ids_for_gasto(
        self,
        gasto_id: int,
        session: AsyncSession
    ) -> List[int]:
        """
        Busca todas las transacciones cuya descripción contenga 'Gasto {gasto_id}'
        y devuelve sus IDs.

        Args:
            gasto_id (int): ID del gasto para filtrar en la descripción.
            session (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            List[int]: Lista de IDs de transacciones que coinciden.
        """
        pattern = f"%Gasto% {gasto_id}%"
        stmt = select(Transaccion.id).where(Transaccion.descripcion.ilike(pattern))
        result = await session.execute(stmt)
        return result.scalars().all()
    
    async def get_transaccion_id_for_pago_compra(
        self,
        pago_id: int,
        compra_id: int,
        session: AsyncSession
    ) -> Optional[int]:
        """
        Busca la transacción automática correspondiente a un abono de compra
        con descripción "<pago_id> Abono compra {compra_id}" y devuelve su ID.

        Args:
            pago_id (int):   ID del DetallePagoCompra.
            compra_id (int): ID de la compra asociada.
            session:        Sesión asíncrona de SQLAlchemy.

        Returns:
            Optional[int]: ID de la transacción si existe, o None.
        """
        pattern = f"{pago_id} Abono compra {compra_id}%"
        stmt = select(Transaccion.id).where(
            Transaccion.descripcion.ilike(pattern)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_transaccion_id_for_pago_venta(
        self,
        pago_id: int,
        venta_id: int,
        session: AsyncSession
    ) -> Optional[int]:
        """
        Busca la transacción automática correspondiente a un abono de venta
        con descripción "<pago_id> Abono venta {venta_id}" y devuelve su ID.

        Args:
            pago_id (int):   ID del DetallePagoVenta.
            venta_id (int):  ID de la venta asociada.
            session:        Sesión asíncrona de SQLAlchemy.

        Returns:
            Optional[int]: ID de la transacción si existe, o None.
        """
        pattern = f"{pago_id} Abono venta {venta_id}%"  
        stmt = select(Transaccion.id).where(
            Transaccion.descripcion.ilike(pattern)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_paginated(
        self,
        offset: int,
        limit: int,
        session: AsyncSession
    ) -> List[Transaccion]:
        stmt = select(Transaccion).offset(offset).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def list_by_banco_paginated(
        self,
        banco_id: int,
        offset: int,
        limit: int,
        session: AsyncSession
    ) -> List[Transaccion]:
        stmt = (
            select(Transaccion)
            .where(Transaccion.banco_id == banco_id)
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def list_by_tipo_paginated(
        self,
        tipo_id: int,
        offset: int,
        limit: int,
        session: AsyncSession
    ) -> List[Transaccion]:
        stmt = (
            select(Transaccion)
            .where(Transaccion.tipo_id == tipo_id)
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def list_by_rango_paginated(
        self,
        fecha_inicio: datetime,
        fecha_fin: datetime,
        offset: int,
        limit: int,
        session: AsyncSession
    ) -> List[Transaccion]:
        stmt = (
            select(Transaccion)
            .where(
                and_(
                    Transaccion.fecha_creacion >= fecha_inicio,
                    Transaccion.fecha_creacion <= fecha_fin
                )
            )
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()