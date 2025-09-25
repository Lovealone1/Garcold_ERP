from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class VentaDTO(BaseModel):
    cliente_id: int
    banco_id: int
    total: float
    estado_id: int
    saldo_restante: Optional[float] = None
    fecha: datetime = field(default_factory=datetime.now)




@dataclass
class VentaListDTO:
    id: int
    cliente: str
    banco: str
    estado: str
    total: float
    saldo_restante: float
    fecha: datetime

@dataclass
class VentasPageDTO:
    items: List[VentaListDTO]
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool
