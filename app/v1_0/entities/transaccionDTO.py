from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TransaccionDTO(BaseModel):
    banco_id: int
    monto: float
    tipo_id: int
    descripcion: Optional[str] = None
    fecha_creacion: datetime = Field(default_factory=datetime.now)
