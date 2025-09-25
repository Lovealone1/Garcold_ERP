from pydantic import BaseModel

class PagoRequestDTO(BaseModel):
    banco_id: int
    monto: float

