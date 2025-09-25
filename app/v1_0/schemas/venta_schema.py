from typing import List
from pydantic import BaseModel, Field

class DetalleCarrito(BaseModel):
    producto_id: int = Field(..., description="ID del producto a vender")
    cantidad: int = Field(..., gt=0, description="Cantidad del producto")
    precio_producto: float = Field(..., gt=0, description="Precio de venta unitario del producto")

class VentaRequestDTO(BaseModel):
    cliente_id: int = Field(..., description="ID del cliente que realiza la compra")
    banco_id: int = Field(..., description="ID del banco asociado al pago")
    estado_id: int = Field(..., description="ID del estado de la venta")
    carrito: List[DetalleCarrito] = Field(..., description="Productos incluidos en la venta")
    

class DetalleVentaCreate(BaseModel):
    venta_id: int
    producto_id: int
    cantidad: int = Field(gt=0)
    precio_producto: float = Field(gt=0)