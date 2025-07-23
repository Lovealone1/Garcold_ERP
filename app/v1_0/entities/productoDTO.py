from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ProductoDTO(BaseModel):
    referencia: str
    descripcion: str
    cantidad: Optional[int] = None
    precio_compra: float
    precio_venta: float
    activo: bool = True
    fecha_creacion: datetime = Field(default_factory=datetime.now)
