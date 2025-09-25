from pydantic import BaseModel, Field

class ProductoRequestDTO(BaseModel):
    """
    DTO para creación o actualización de un producto.
    """
    referencia: str = Field(..., description="Código único de referencia del producto")
    descripcion: str = Field(..., description="Descripción del producto")
    precio_compra: float = Field(..., ge=0, description="Precio de compra")
    precio_venta: float = Field(..., ge=0, description="Precio de venta")
    cantidad: int = Field(..., ge=0, description="Cantidad en stock inicial")
