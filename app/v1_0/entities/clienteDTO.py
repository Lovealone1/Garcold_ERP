from pydantic import BaseModel, EmailStr, Field
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

class ClienteDTO(BaseModel):
    cc_nit: str
    nombre: str
    direccion: str
    ciudad: str
    celular: Optional[str] = None
    correo: Optional[EmailStr] = None
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    saldo: Optional[float] = None

@dataclass
class ClienteListDTO:
    """DTO para el listado de clientes, con todos sus campos."""
    id: int
    nombre: str
    cc_nit: str
    correo: Optional[str]
    celular: Optional[str]
    direccion: str
    ciudad: str
    saldo: float
    fecha_creacion: datetime


@dataclass
class ListClienteDTO: 
    id: int
    nombre: str 

@dataclass
class ClientesPageDTO:
    """DTO para encapsular paginación de clientes."""
    items: List[ClienteListDTO]
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool