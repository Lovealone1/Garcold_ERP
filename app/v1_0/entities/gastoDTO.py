from pydantic import BaseModel
from datetime import date

class GastoDTO(BaseModel):
    categoria_gasto_id: int
    monto: float
    banco_id: int
    fecha_gasto: date
