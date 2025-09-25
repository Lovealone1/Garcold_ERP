from pydantic import BaseModel, Field
from datetime import datetime
from dataclasses import dataclass

class DetallePagoVentaDTO(BaseModel):
    venta_id: int
    banco_id: int
    monto: float
    fecha_creacion: datetime = Field(default_factory=datetime.now)

@dataclass
class PagoResponseDTO:
    id: int
    venta_id: int
    banco: str
    saldo_restante: float
    monto_abonado: float
    fecha_creacion: datetime
