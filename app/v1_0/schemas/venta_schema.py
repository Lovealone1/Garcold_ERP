from typing import List
from pydantic import BaseModel, Field
from datetime import datetime

class DetalleVentaResponse(BaseModel):
    producto_id: int
    cantidad: int
    precio_producto: float
    total: float

class VentaResponse(BaseModel):
    id: int
    cliente: str
    banco: str
    estado: str
    total: float
    saldo_restante: float
    fecha: datetime

class DetalleCarrito(BaseModel):
    producto_id: int = Field(..., description="ID del producto a vender")
    cantidad: int = Field(..., gt=0, description="Cantidad del producto")
    precio_producto: float = Field(..., gt=0, description="Precio de venta unitario del producto")


class VentaRequestDTO(BaseModel):
    cliente_id: int = Field(..., description="ID del cliente que realiza la compra")
    banco_id: int = Field(..., description="ID del banco asociado al pago")
    estado_id: int = Field(..., description="ID del estado de la venta (ej. venta contado, venta crédito)")
    carrito: List[DetalleCarrito] = Field(..., description="Lista de productos incluidos en la venta")

    class Config:
        schema_extra = {
            "example": {
                "cliente_id": 1,
                "banco_id": 1,
                "estado_id": 3,
                "carrito": [
                    {
                        "producto_id": 101,
                        "cantidad": 2,
                        "precio_producto": 5000.0
                    },
                    {
                        "producto_id": 102,
                        "cantidad": 1,
                        "precio_producto": 7000.0
                    }
                ]
            }
        }
