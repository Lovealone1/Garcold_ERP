from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class VentaDTO(BaseModel):
    cliente_id: int
    banco_id: int
    total: float
    estado_id: int
    saldo_restante: Optional[float] = None
    fecha: datetime = Field(default_factory=datetime.now)
