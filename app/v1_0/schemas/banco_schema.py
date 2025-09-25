from pydantic import BaseModel, Field

class BancoCreateSchema(BaseModel):
    """
    Schema para crear un nuevo Banco.
    Solo requiere el nombre y el saldo inicial.
    """
    nombre: str = Field(..., min_length=1, max_length=100)
    saldo: float = Field(..., ge=0, description="Saldo inicial del banco")

    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Banco Central",
                "saldo": 0.0
            }
        }

class BancoUpdateSaldoSchema(BaseModel):
    nuevo_saldo: float = Field(..., ge=0)