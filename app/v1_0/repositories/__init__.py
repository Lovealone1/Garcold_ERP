from .base_repository import BaseRepository
from .cliente_repository import ClienteRepository
from .banco_repository import BancoRepository
from .producto_repository import ProductoRepository
from .venta_repository import VentaRepository
from .detalle_venta_repository import DetalleVentaRepository
from .detalle_utilidad_repository import DetalleUtilidadRepository
from .utiliadad_repository import UtilidadRepository
from .estado_repository import EstadoRepository
from .compra_repository import CompraRepository
from .detalle_compra_repository import DetalleCompraRepository
from .proveedor_repository import ProveedorRepository
from .detalle_pago_venta_repository import DetallePagoVentaRepository
from .detalle_pago_compra_repository import DetallePagoCompraRepository
from .gasto_repository import GastoRepository
from .categoria_gasto_repository import CategoriaGastosRepository
from .credito_repository import CreditoRepository
from .inversion_repository import InversionRepository
from .tipo_transaccion_repository import TipoTransaccionRepository
from .transaccion_repository import TransaccionRepository
from .user_repository import UserRepository
__all__ = [
    "BaseRepository",
    "ClienteRepository",
    "BancoRepository",
    "ProductoRepository",
    "VentaRepository",
    "DetalleVentaRepository",
    "DetalleUtilidadRepository",
    "UtilidadRepository",
    "EstadoRepository",
    "CompraRepository",
    "DetalleCompraRepository",
    "ProveedorRepository",
    "DetallePagoVentaRepository",
    "DetallePagoCompraRepository",
    "GastoRepository",
    "CategoriaGastosRepository",
    "CreditoRepository",
    "InversionRepository",
    "TipoTransaccionRepository",
    "TransaccionRepository",
    "UserRepository"
]
