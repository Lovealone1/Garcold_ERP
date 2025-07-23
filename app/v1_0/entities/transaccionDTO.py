from pydantic import BaseModel, Field
from datetime import datetime

class TransaccionDTO(BaseModel):
    banco_id: int
    monto: float
    tipo_id: int
    fecha_creacion: datetime = Field(default_factory=datetime.now)
