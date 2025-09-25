from pydantic import BaseModel, Field
from datetime import date
class CreditoRequestDTO(BaseModel):
    """
    DTO para creación o actualización de un crédito.
    """
    nombre: str = Field(..., description="Nombre del crédito")
    monto: float = Field(..., gt=0, description="Monto inicial o actualizado del crédito")


class CreditoResponseDTO(BaseModel):
    """
    DTO de respuesta para un crédito.
    """
    id: int = Field(..., description="ID del crédito")
    nombre: str = Field(..., description="Nombre del crédito")
    monto: float = Field(..., description="Monto actual del crédito")
    fecha_creacion: date = Field(..., description="Fecha de vencimiento del credito")
