from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class BancoDTO(BaseModel):
    id: int
    nombre: str
    saldo: float
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    fecha_actualizacion: Optional[datetime] = None