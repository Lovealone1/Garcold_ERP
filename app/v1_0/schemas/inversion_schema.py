from pydantic import BaseModel, Field
from datetime import date

class InversionRequestDTO(BaseModel):
    """
    DTO para creación o actualización de una inversión.
    """
    nombre: str = Field(..., description="Nombre de la inversión")
    saldo: float = Field(..., gt=0, description="Saldo inicial o actualizado de la inversión")
    fecha_vencimiento: date = Field(
        ...,
        description="Fecha de vencimiento de la inversión (YYYY‑MM‑DD)"
    )

class InversionUpdateDTO(BaseModel):
    saldo: float = Field(..., gt=0, description="Nuevo saldo de la inversión")

class InversionResponseDTO(BaseModel):
    """
    DTO de respuesta para una inversión.
    """
    id: int = Field(..., description="ID de la inversión")
    nombre: str = Field(..., description="Nombre de la inversión")
    saldo: float = Field(..., description="Saldo actual de la inversión")
    fecha_vencimiento: date = Field(..., description="Fecha de vencimiento de la inversión")
