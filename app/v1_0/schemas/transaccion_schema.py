from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TransaccionResponseDTO(BaseModel):
    """
    DTO de salida para transacciones manuales (ingresos/retiros).
    """
    id: int = Field(..., description="ID de la transacción")
    banco: str = Field(..., description="Nombre del banco afectado")
    tipo: str = Field(..., description="Nombre del tipo de transacción")
    monto: float = Field(..., description="Monto de la transacción")
    descripcion: Optional[str] = Field(None, description="Descripción libre de la transacción")  
    fecha_creacion: datetime = Field(..., description="Fecha y hora de creación")