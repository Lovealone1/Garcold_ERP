from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ClienteListDTO(BaseModel):
    """
    DTO para el listado completo de clientes, con todos sus campos.
    """
    id: int
    nombre: str
    cc_nit: str
    correo: Optional[str] = None
    celular: Optional[str] = None
    direccion: str
    ciudad: str
    saldo: float
    fecha_creacion: datetime

class ClienteRequestDTO(BaseModel):
    """
    DTO para creación o actualización de un cliente.
    """
    nombre: str = Field(..., description="Nombre completo del cliente")
    cc_nit: str = Field(..., description="Número de cédula o NIT del cliente")
    correo: Optional[str] = Field(None, description="Correo electrónico del cliente")
    celular: Optional[str] = Field(None, description="Número de celular (solo dígitos)")
    direccion: str = Field(..., description="Dirección del cliente")
    ciudad: str = Field(..., description="Ciudad de residencia del cliente")
    saldo: Optional[float] = Field(0.0, ge=0, description="Saldo inicial del cliente")