from typing import List
from pydantic import BaseModel, Field
from datetime import datetime


class DetalleCompraResponse(BaseModel):
    producto_id: int
    cantidad: int
    precio_compra: float
    total: float


class CompraResponse(BaseModel):
    id: int
    proveedor: str
    banco: str
    estado: str
    total: float
    fecha: datetime


class DetalleCompraCarrito(BaseModel):
    producto_id: int = Field(..., description="ID del producto a comprar")
    cantidad: int = Field(..., gt=0, description="Cantidad del producto")
    precio: float = Field(..., gt=0, description="Precio de compra unitario del producto")


class CompraRequestDTO(BaseModel):
    proveedor_id: int = Field(..., description="ID del proveedor")
    banco_id: int = Field(..., description="ID del banco asociado al pago")
    estado_id: int = Field(..., description="ID del estado de la compra (ej. contado, crédito)")
    carrito: List[DetalleCompraCarrito] = Field(..., description="Lista de productos incluidos en la compra")

    class Config:
        schema_extra = {
            "example": {
                "proveedor_id": 1,
                "banco_id": 1,
                "estado_id": 4,
                "carrito": [
                    {
                        "producto_id": 27,
                        "cantidad": 1,
                        "precio_compra": 2400.0
                    },
                    {
                        "producto_id": 28,
                        "cantidad": 2,
                        "precio_compra": 3500.0
                    }
                ]
            }
        }
