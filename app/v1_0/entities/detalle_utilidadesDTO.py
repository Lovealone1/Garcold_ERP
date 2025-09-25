from pydantic import BaseModel
from typing import Optional

class DetalleUtilidadDTO(BaseModel):
    venta_id: int
    producto_id: int
    referencia: Optional[str] = None
    descripcion: Optional[str] = None
    cantidad: int
    precio_compra: float
    precio_venta: float
    total_utilidad: float
