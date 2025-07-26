from pydantic import BaseModel, Field
from datetime import date
from typing import Optional
from datetime import datetime

class CompraDTO(BaseModel):
    fecha_compra: datetime = Field(default_factory=datetime.now)
    proveedor_id: int
    total: float
    banco_id: int
    estado_id: int
    saldo: Optional[float] = None