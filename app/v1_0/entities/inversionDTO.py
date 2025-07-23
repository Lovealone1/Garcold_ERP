from pydantic import BaseModel
from datetime import date

class InversionDTO(BaseModel):
    nombre: str
    saldo: float
    fecha_vencimiento: date
