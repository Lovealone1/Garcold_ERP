from dependency_injector import containers, providers

from app.v1_0.repositories import (
    VentaRepository,
    DetalleVentaRepository,
    ProductoRepository,
    ClienteRepository,
    EstadoRepository,
    DetalleUtilidadRepository,
    UtilidadRepository,
    BancoRepository,
    CompraRepository,
    DetalleCompraRepository,
    ProveedorRepository,
    DetallePagoVentaRepository,
    DetallePagoCompraRepository
)
from app.v1_0.services.venta_service import VentaService
from app.v1_0.services.compra_service import CompraService
from app.v1_0.services.pago_venta_service import PagoVentaService

class APIContainer(containers.DeclarativeContainer):
    """
    Contenedor para repositorios y servicios de la API de ventas.
    """

    # Repositorios ya no reciben session_factory
    venta_repository = providers.Singleton(VentaRepository)
    detalle_venta_repository = providers.Singleton(DetalleVentaRepository)
    producto_repository = providers.Singleton(ProductoRepository)
    cliente_repository = providers.Singleton(ClienteRepository)
    estado_repository = providers.Singleton(EstadoRepository)
    detalle_utilidad_repository = providers.Singleton(DetalleUtilidadRepository)
    utilidad_repository = providers.Singleton(UtilidadRepository)
    banco_repository = providers.Singleton(BancoRepository)
    compra_repository = providers.Singleton(CompraRepository)
    detalle_compra_repository = providers.Singleton(DetalleCompraRepository)
    proveedor_repository = providers.Singleton(ProveedorRepository)
    detalle_pago_venta_repository = providers.Singleton(DetallePagoVentaRepository)
    detalle_pago_compra_repository = providers.Singleton(DetallePagoCompraRepository)

    # Servicios
    venta_service = providers.Singleton(
        VentaService,
        venta_repository=venta_repository,
        detalle_repository=detalle_venta_repository,
        producto_repository=producto_repository,
        cliente_repository=cliente_repository,
        estado_repository=estado_repository,
        detalle_utilidad_repository=detalle_utilidad_repository,
        utilidad_repository=utilidad_repository,
        banco_repository=banco_repository,
    )

    compra_service = providers.Singleton(
        CompraService,
        compra_repository=compra_repository,
        detalle_repository=detalle_compra_repository,
        producto_repository=producto_repository,
        banco_repository=banco_repository,
        proveedor_repository=proveedor_repository,
        estado_repository=estado_repository,
    )

    pago_venta_service = providers.Singleton(
        PagoVentaService,
        venta_repository=venta_repository,
        compra_repository=compra_repository,
        estado_repository=estado_repository,
        pago_venta_repository=detalle_pago_venta_repository, 
        pago_compra_repository=detalle_pago_compra_repository,
        banco_repository=banco_repository
    )