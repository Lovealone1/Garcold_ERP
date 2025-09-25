from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from dataclasses import dataclass
from typing import List

class TransaccionDTO(BaseModel):
    banco_id: int
    monto: float
    tipo_id: int
    descripcion: Optional[str] = None
    fecha_creacion: datetime = Field(default_factory=datetime.now)

@dataclass
class TransaccionListDTO:
    """
    DTO para el listado de transacciones.
    """
    id: int
    banco_id: int
    monto: float
    tipo_id: int
    descripcion: Optional[str]
    fecha_creacion: datetime

@dataclass
class TransaccionResponseDTO:
    """
    DTO para el listado de transacciones.
    """
    id: int
    banco_id: int
    monto: float
    tipo_str: str
    descripcion: Optional[str]
    fecha_creacion: datetime

@dataclass
class TransaccionPageDTO:
    """DTO para encapsular paginación de transacciones."""
    items: List[TransaccionResponseDTO]
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool