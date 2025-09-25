from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from dataclasses import dataclass

class UtilidadDTO(BaseModel):
    venta_id: int
    utilidad: float
    fecha: datetime = Field(default_factory=datetime.now)

@dataclass
class UtilidadListDTO:
    """
    DTO para el listado de utilidades.
    """
    id: int
    venta_id: int
    utilidad: float
    fecha: datetime

@dataclass
class UtilidadPageDTO:
    """DTO para encapsular paginación de clientes."""
    items: List[UtilidadListDTO]
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool