from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector.wiring import inject, Provide
from datetime import datetime

from app.utils.database.db_connector import get_db
from app.app_containers import ApplicationContainer
from app.v1_0.schemas.transaccion_schema import TransaccionResponseDTO

router = APIRouter(
    prefix="/transacciones",
    tags=["Transacciones"],
)


@router.post(
    "/crear",
    response_model=TransaccionResponseDTO,
    summary="Registra una nueva transacción y ajusta el saldo del banco"
)
@inject
async def crear_transaccion(
    banco_id: int,
    tipo_id: int,
    monto: float,
    descripcion: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    transaccion_service=Depends(Provide[ApplicationContainer.api_container.transaccion_service])
):
    """
    Persiste una transacción y ajusta el saldo del banco según el tipo:
      - 'Ingreso'  (tipo_id señala un tipo con nombre 'Ingreso'): aumenta saldo
      - 'Retiro'   (tipo_id señala un tipo con nombre 'Retiro'): disminuye saldo (verifica fondos)

    Args:
        banco_id:     ID del banco.
        tipo_id:      ID del tipo de transacción.
        monto:        Monto positivo de la transacción.
        descripcion:  Texto opcional que describe el movimiento.
        db:           Sesión asíncrona de SQLAlchemy.

    Raises:
        HTTPException 400: monto inválido, tipo no soportado o fondos insuficientes.
        HTTPException 404: banco o tipo no encontrados.

    Returns:
        TransaccionResponseDTO: DTO con los datos de la transacción creada.
    """
    if monto <= 0:
        raise HTTPException(status_code=400, detail="El monto debe ser mayor que cero")

    return await transaccion_service.crear_transaccion(
        banco_id=banco_id,
        tipo_id=tipo_id,
        monto=monto,
        descripcion=descripcion,
        db=db
    )


@router.delete(
    "/eliminar/{transaccion_id}",
    response_model=dict,
    summary="Elimina una transacción manual y, si es de tipo Retiro/Ingreso, revierte saldo"
)
@inject
async def eliminar_transaccion(
    transaccion_id: int,
    db: AsyncSession = Depends(get_db),
    transaccion_service=Depends(Provide[ApplicationContainer.api_container.transaccion_service])
):
    """
    Elimina una transacción manual:
      - Si es del libro mayor (registrar_transaccion), solo borra el asiento.
      - Si fue creada con ajuste de saldo (crear_transaccion), revierte el débito/crédito en el banco.

    Args:
        transaccion_id: ID de la transacción a eliminar.
        db:             Sesión asíncrona de SQLAlchemy.

    Raises:
        HTTPException 404: Si no existe la transacción.

    Returns:
        dict: Mensaje de confirmación.
    """
    deleted = await transaccion_service.eliminar_transaccion_manual(
        transaccion_id=transaccion_id, db=db
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    return {"mensaje": f"Transacción con ID {transaccion_id} eliminada correctamente"}

@router.get(
"/",
response_model=List[TransaccionResponseDTO],
summary="Lista todas las transacciones (paginado, 10 por página)"
)
    
@inject
async def listar_transacciones(
    page: int = Query(1, ge=1, description="Número de página (1-based)"),
    db: AsyncSession = Depends(get_db),
    transaccion_service=Depends(Provide[ApplicationContainer.api_container.transaccion_service])
):
    return await transaccion_service.listar_transacciones(page=page, session=db)


@router.get(
    "/banco/{banco_id}",
    response_model=List[TransaccionResponseDTO],
    summary="Lista transacciones de un banco (paginado, 10 por página)"
)
@inject
async def listar_por_banco(
    banco_id: int,
    page: int = Query(1, ge=1, description="Número de página (1-based)"),
    db: AsyncSession = Depends(get_db),
    transaccion_service=Depends(Provide[ApplicationContainer.api_container.transaccion_service])
):
    return await transaccion_service.listar_por_banco(banco_id=banco_id, page=page, session=db)


@router.get(
    "/tipo/{tipo_id}",
    response_model=List[TransaccionResponseDTO],
    summary="Lista transacciones de un tipo (paginado, 10 por página)"
)
@inject
async def listar_por_tipo(
    tipo_id: int,
    page: int = Query(1, ge=1, description="Número de página (1-based)"),
    db: AsyncSession = Depends(get_db),
    transaccion_service=Depends(Provide[ApplicationContainer.api_container.transaccion_service])
):
    return await transaccion_service.listar_por_tipo(tipo_id=tipo_id, page=page, session=db)


@router.get(
    "/rango",
    response_model=List[TransaccionResponseDTO],
    summary="Lista transacciones en un rango de fechas (paginado, 10 por página)"
)
@inject
async def listar_por_rango(
    fecha_inicio: datetime = Query(..., description="Fecha y hora inicio ISO-8601"),
    fecha_fin:    datetime = Query(..., description="Fecha y hora fin ISO-8601"),
    page:         int      = Query(1, ge=1, description="Número de página (1-based)"),
    db: AsyncSession          = Depends(get_db),
    transaccion_service       = Depends(Provide[ApplicationContainer.api_container.transaccion_service])
):
    return await transaccion_service.listar_por_rango(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        page=page,
        session=db
    )