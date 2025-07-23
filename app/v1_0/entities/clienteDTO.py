from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class ClienteDTO(BaseModel):
    cc_nit: str
    nombre: str
    direccion: str
    ciudad: str
    celular: Optional[str] = None
    correo: Optional[EmailStr] = None
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    saldo: Optional[float] = None
