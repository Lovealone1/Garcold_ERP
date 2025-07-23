from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class ProveedorDTO(BaseModel):
    cc_nit: str
    nombre: str
    direccion: str
    ciudad: str
    celular: Optional[str] = None
    correo: Optional[EmailStr] = None
    fecha_creacion: Optional[datetime] = None
