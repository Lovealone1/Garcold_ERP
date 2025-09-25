from pydantic import BaseModel

class EstadoDTO(BaseModel):
    id: int
    nombre: str
