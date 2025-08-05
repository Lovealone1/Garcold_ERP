from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional

class ProveedorListDTO(BaseModel):
    """
    DTO para el listado completo de proveedores.
    """
    id: int
    cc_nit: str
    nombre: str
    direccion: str
    ciudad: str
    celular: Optional[str] = None
    correo: Optional[str] = None
    fecha_creacion: datetime

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