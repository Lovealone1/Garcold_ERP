from dependency_injector import containers, providers

from app.v1_0.repositories import (
    VentaRepository,
    DetalleVentaRepository,
    ProductoRepository,
    ClienteRepository,
    EstadoRepository,
    DetalleUtilidadRepository,
    UtilidadRepository,
    BancoRepository
)

from app.v1_0.services.venta_service import VentaService


class APIContainer(containers.DeclarativeContainer):
    """
    Contenedor para registrar los repositorios y servicios de la API de ventas.
    """

    db_session = providers.Dependency()

    venta_repository = providers.Singleton(VentaRepository, session_factory=db_session)
    detalle_venta_repository = providers.Singleton(DetalleVentaRepository, session_factory=db_session)
    producto_repository = providers.Singleton(ProductoRepository, session_factory=db_session)
    cliente_repository = providers.Singleton(ClienteRepository, session_factory=db_session)
    estado_repository = providers.Singleton(EstadoRepository, session_factory=db_session)
    detalle_utilidad_repository = providers.Singleton(DetalleUtilidadRepository, session_factory=db_session)
    utilidad_repository = providers.Singleton(UtilidadRepository, session_factory=db_session)
    banco_repository = providers.Singleton(BancoRepository, session_factory=db_session)

    venta_service = providers.Singleton(
        VentaService,
        venta_repository=venta_repository,
        detalle_repository=detalle_venta_repository,
        producto_repository=producto_repository,
        cliente_repository=cliente_repository,
        estado_repository=estado_repository,
        detalle_utilidad_repository=detalle_utilidad_repository,
        utilidad_repository=utilidad_repository,
        banco_repository=banco_repository
    )
