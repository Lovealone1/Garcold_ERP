from pydantic import BaseModel, Field
from datetime import date


class GastoRequestDTO(BaseModel):
    """
    DTO para la creación de un gasto.
    """
    categoria_gasto_id: int = Field(..., description="ID de la categoría del gasto")
    banco_id: int = Field(..., description="ID del banco desde el cual se realiza el gasto")
    monto: float = Field(..., gt=0, description="Monto del gasto (debe ser mayor que 0)")
    fecha_gasto: date = Field(..., description="Fecha en que se realiza el gasto")


class GastoResponseDTO(BaseModel):
    """
    DTO de respuesta para un gasto, incluyendo nombres de banco y categoría.
    """
    id: int = Field(..., description="ID del gasto")
    categoria: str = Field(..., description="Nombre de la categoría del gasto")
    banco: str = Field(..., description="Nombre del banco asociado al gasto")
    monto: float = Field(..., description="Monto del gasto")
    fecha_gasto: date = Field(..., description="Fecha en que se realizó el gasto")
