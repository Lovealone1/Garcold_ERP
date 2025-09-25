from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class ProveedorRequestDTO(BaseModel):
    """
    DTO para creación o actualización de un proveedor.
    """
    cc_nit: str = Field(..., description="Número de cédula o NIT del proveedor")
    nombre: str = Field(..., description="Nombre del proveedor")
    direccion: str = Field(..., description="Dirección del proveedor")
    ciudad: str = Field(..., description="Ciudad del proveedor")
    celular: Optional[str] = Field(None, description="Número de celular (solo dígitos)")
    correo: Optional[EmailStr] = Field(None, description="Correo electrónico")