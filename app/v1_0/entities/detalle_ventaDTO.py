from pydantic import BaseModel
from dataclasses import dataclass

class DetalleVentaDTO(BaseModel):
    producto_id: int
    cantidad: int
    precio_producto: float
    total: float
    venta_id: int

@dataclass
class DetalleVentaViewDTO:
    venta_id: int
    producto_referencia: str
    cantidad: int
    precio: float
    total: float