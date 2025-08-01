from typing import List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1_0.entities import GastoDTO, TransaccionDTO
from app.v1_0.schemas.gasto_schema import GastoResponseDTO
from app.v1_0.repositories import (
    GastoRepository,
    BancoRepository,
    CategoriaGastosRepository,
)
from app.v1_0.services.transaccion_service import TransaccionService

class GastoService:
    """
    Servicio para gestionar registros de gastos.
    """

    def __init__(
        self,
        gasto_repository: GastoRepository,
        banco_repository: BancoRepository,
        categoria_repository: CategoriaGastosRepository,
        transaccion_service: TransaccionService,
    ):
        """
        Inicializa el servicio con los repositorios necesarios.

        Args:
            gasto_repository: Repositorio para CRUD de gastos.
            banco_repository: Repositorio para consultar y modificar bancos.
            categoria_repository: Repositorio para consultar categorías de gasto.
        """
        self.gasto_repo = gasto_repository
        self.banco_repo = banco_repository
        self.categoria_repo = categoria_repository
        self.transaccion_service = transaccion_service
    async def crear_gasto(
        self,
        gasto_dto: GastoDTO,
        db: AsyncSession
    ) -> GastoResponseDTO:
        """
        Registra un nuevo gasto y descuenta su monto del saldo del banco.

        Args:
            gasto_dto (GastoDTO): DTO con los datos del gasto a crear.
            db (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            GastoResponseDTO: DTO con los datos del gasto creado y nombre de banco y categoría.

        Raises:
            HTTPException 404: Si el banco o la categoría no existen.
            HTTPException 400: Si el monto es inválido o excede el saldo del banco.
        """
        async with db.begin():
            banco = await self.banco_repo.get_by_id(gasto_dto.banco_id, session=db)
            if not banco:
                raise HTTPException(404, "Banco no encontrado")
            categoria = await self.categoria_repo.get_by_id(
                gasto_dto.categoria_gasto_id, session=db
            )
            if not categoria:
                raise HTTPException(404, "Categoría de gasto no encontrada")
            if gasto_dto.monto <= 0:
                raise HTTPException(400, "El monto del gasto debe ser mayor que cero")
            if banco.saldo < gasto_dto.monto:
                raise HTTPException(
                    400,
                    f"Saldo insuficiente en el banco ({banco.saldo:.2f})"
                )
            await self.banco_repo.disminuir_saldo(
                gasto_dto.banco_id, gasto_dto.monto, session=db
            )
            gasto = await self.gasto_repo.create_gasto(gasto_dto, session=db)

            await self.transaccion_service.insertar_transaccion(
                            TransaccionDTO(
                                banco_id=gasto_dto.banco_id,
                                monto=gasto_dto.monto,
                                tipo_id=5,  # 5 = Gasto
                                descripcion=f"Gasto {categoria.nombre} {gasto.id}"
                            ),
                            db=db
                        )

        return GastoResponseDTO(
            id=gasto.id,
            categoria=categoria.nombre,
            banco=banco.nombre,
            monto=gasto.monto,
            fecha_gasto=gasto.fecha_gasto
        )

    async def listar_gastos_por_categoria(
        self,
        categoria_id: int,
        db: AsyncSession
    ) -> List[GastoResponseDTO]:
        """
        Obtiene todos los gastos de una categoría específica.

        Args:
            categoria_id (int): ID de la categoría de gasto.
            db (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            List[GastoResponseDTO]: Lista de DTOs con información de cada gasto.
        """
        gastos = await self.gasto_repo.get_by_categoria(categoria_id, session=db)
        result: List[GastoResponseDTO] = []

        categoria = await self.categoria_repo.get_by_id(categoria_id, session=db)
        nombre_categoria = categoria.nombre if categoria else "Desconocida"

        for gasto in gastos:
            banco = await self.banco_repo.get_by_id(gasto.banco_id, session=db)
            result.append(GastoResponseDTO(
                id=gasto.id,
                categoria=nombre_categoria,
                banco=banco.nombre if banco else "Desconocido",
                monto=gasto.monto,
                fecha_gasto=gasto.fecha_gasto
            ))
        return result

    async def eliminar_gasto(
        self,
        gasto_id: int,
        db: AsyncSession
    ) -> bool:
        """
        Elimina un gasto y devuelve su monto al saldo del banco.

        Args:
            gasto_id (int): ID del gasto a eliminar.
            db (AsyncSession): Sesión asíncrona de SQLAlchemy.

        Returns:
            bool: True si el gasto existía y se eliminó; False en caso contrario.

        Raises:
            HTTPException 404: Si el gasto o el banco no existen.
        """
        async with db.begin():
            gasto = await self.gasto_repo.get_by_id(gasto_id, session=db)
            if not gasto:
                return False

            banco = await self.banco_repo.get_by_id(gasto.banco_id, session=db)
            if not banco:
                raise HTTPException(404, "Banco asociado al gasto no encontrado")

            await self.banco_repo.aumentar_saldo(
                gasto.banco_id, gasto.monto, session=db
            )
            deleted = await self.gasto_repo.delete_gasto(gasto_id, session=db)
            await self.transaccion_service.eliminar_transacciones_gasto(gasto_id, db=db)
            return deleted
