from pydantic import BaseModel, Field
from datetime import datetime

class DetalleVentaDTO(BaseModel):
    producto_id: int
    cantidad: int
    precio_producto: float
    total: float
    venta_id: int

