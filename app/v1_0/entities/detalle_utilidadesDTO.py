from pydantic import BaseModel

class DetalleUtilidadDTO(BaseModel):
    venta_id: int
    producto_id: int
    cantidad: int
    precio_compra: float
    precio_venta: float
    total_utilidad: float
