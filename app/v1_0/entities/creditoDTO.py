from pydantic import BaseModel, Field
from datetime import datetime

class CreditoDTO(BaseModel):
    nombre: str
    monto: float
    fecha_creacion: datetime = Field(default_factory=datetime.now)
