from pydantic import BaseModel
from datetime import date
from typing import Optional

class CompraDTO(BaseModel):
    fecha_compra: date
    proveedor_id: int
    total: float
    banco_id: int
    estado_id: int
    saldo: Optional[float] = None