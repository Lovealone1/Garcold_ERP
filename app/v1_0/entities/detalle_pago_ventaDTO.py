from pydantic import BaseModel, Field
from datetime import datetime

class DetallePagoVentaDTO(BaseModel):
    venta_id: int
    banco_id: int
    monto: float
    fecha_creacion: datetime = Field(default_factory=datetime.now)
