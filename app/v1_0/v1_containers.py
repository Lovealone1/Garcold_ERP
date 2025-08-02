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
    DetallePagoCompraRepository, 
    GastoRepository,
    CategoriaGastosRepository,
    CreditoRepository, 
    InversionRepository, 
    TipoTransaccionRepository,
    TransaccionRepository
)
from app.v1_0.services.venta_service import VentaService
from app.v1_0.services.compra_service import CompraService
from app.v1_0.services.pago_venta_service import PagoVentaService
from app.v1_0.services.pago_compra_service import PagoCompraService
from app.v1_0.services.gasto_service import GastoService
from app.v1_0.services.credito_service import CreditoService
from app.v1_0.services.inversion_service import InversionService
from app.v1_0.services.transaccion_service import TransaccionService
from app.v1_0.services.producto_service import ProductoService
class APIContainer(containers.DeclarativeContainer):
    """
    Contenedor para repositorios y servicios de la API de ventas.
    """
    # Repositorios
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
    gasto_repository = providers.Singleton(GastoRepository)
    categoria_gastos_repository = providers.Singleton(CategoriaGastosRepository)
    credito_repository = providers.Singleton(CreditoRepository)
    inversion_repository = providers.Singleton(InversionRepository)
    tipo_transaccion_repository = providers.Singleton(TipoTransaccionRepository)
    transaccion_repository = providers.Singleton(TransaccionRepository)

    # Servicios
    producto_service = providers.Singleton(
        ProductoService,
        producto_repository=producto_repository
    )

    credito_service = providers.Singleton(
        CreditoService,
        credito_repository=credito_repository
    )

    inversion_service = providers.Singleton(
        InversionService,
        inversion_repository=inversion_repository
    )

    transaccion_service = providers.Singleton(
        TransaccionService,
        transaccion_repository=transaccion_repository,
        tipo_transaccion_repository=tipo_transaccion_repository,
        banco_repository=banco_repository
    )

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
        pago_venta_repository=detalle_pago_venta_repository,
        transaccion_service=transaccion_service
    )

    compra_service = providers.Singleton(
        CompraService,
        compra_repository=compra_repository,
        detalle_repository=detalle_compra_repository,
        producto_repository=producto_repository,
        banco_repository=banco_repository,
        proveedor_repository=proveedor_repository,
        estado_repository=estado_repository,
        pago_compra_repository=detalle_pago_compra_repository,
        transaccion_service=transaccion_service
    )

    gasto_service = providers.Singleton(
        GastoService,  
        gasto_repository=gasto_repository,
        banco_repository=banco_repository,
        categoria_repository=categoria_gastos_repository,
        transaccion_service=transaccion_service
    )

    pago_compra_service = providers.Singleton(
        PagoCompraService,
        compra_repository=compra_repository,
        estado_repository=estado_repository,
        pago_compra_repository=detalle_pago_compra_repository,
        banco_repository=banco_repository,
        transaccion_service=transaccion_service
    )

    pago_venta_service = providers.Singleton(
        PagoVentaService,
        venta_repository=venta_repository,
        estado_repository=estado_repository,
        pago_venta_repository=detalle_pago_venta_repository,
        banco_repository=banco_repository,
        transaccion_service=transaccion_service
    )