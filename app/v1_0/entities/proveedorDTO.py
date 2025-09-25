from pydantic import BaseModel, EmailStr, Field
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


class ProveedorDTO(BaseModel):
    """DTO para la creación/actualización de proveedores."""
    cc_nit: str
    nombre: str
    direccion: str
    ciudad: str
    celular: Optional[str] = None
    correo: Optional[EmailStr] = None
    fecha_creacion: datetime = Field(default_factory=datetime.now)

@dataclass
class ProveedorListDTO:
    """DTO para el listado de proveedores, con todos sus campos."""
    id: int
    nombre: str
    cc_nit: str
    correo: Optional[str]
    celular: Optional[str]
    direccion: str
    ciudad: str
    fecha_creacion: datetime

@dataclass
class ProveedoresPageDTO:
    """DTO para encapsular paginación de proveedores."""
    items: List[ProveedorListDTO]
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool
