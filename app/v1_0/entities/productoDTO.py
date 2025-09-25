from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

class ProductoDTO(BaseModel):
    referencia: str
    descripcion: str
    cantidad: Optional[int] = None
    precio_compra: float
    precio_venta: float
    activo: bool = True
    fecha_creacion: datetime = Field(default_factory=datetime.now)

@dataclass
class ProductoListDTO:
    """
    DTO para el listado completo de productos, con todos sus campos.
    """
    id: int
    referencia: str
    descripcion: str
    cantidad: int
    precio_compra: float
    precio_venta: float
    activo: bool
    fecha_creacion: datetime

@dataclass
class ProductosPageDTO:
    """
    DTO de paginación para productos.
    """
    items: List[ProductoListDTO]
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool
