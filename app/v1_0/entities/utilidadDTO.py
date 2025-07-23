from pydantic import BaseModel, Field
from datetime import datetime

class UtilidadDTO(BaseModel):
    venta_id: int
    utilidad: float
    fecha: datetime = Field(default_factory=datetime.now)
