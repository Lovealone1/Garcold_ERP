from pydantic import BaseModel
from datetime import datetime

class UtilidadListDTO(BaseModel):
    """
    DTO para el listado de utilidades.
    """
    id: int
    venta_id: int
    utilidad: float
    fecha: datetime
