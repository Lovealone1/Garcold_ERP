from pydantic import BaseModel, Field
from datetime import datetime

class DetalleCompraDTO(BaseModel):
    producto_id: int
    cantidad: int
    precio: float
    total: float
    compra_id: int
    fecha_creacion: datetime = Field(default_factory=datetime.now)
