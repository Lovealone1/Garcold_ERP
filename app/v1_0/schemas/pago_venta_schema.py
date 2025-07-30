from datetime import datetime
from pydantic import BaseModel

class PagoRequestDTO(BaseModel):
    banco_id: int
    monto: float

class PagoResponseDTO(BaseModel):
    id: int
    venta_id: int
    banco: str
    saldo_restante: float
    monto_abonado: float
    fecha_creacion: datetime
