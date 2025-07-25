from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class DetalleVenta(Base):
    __tablename__ = "detalle_venta"

    id = Column(Integer, primary_key=True, autoincrement=True)
    producto_id = Column(Integer, ForeignKey("producto.id"), nullable=False)
    venta_id = Column(Integer, ForeignKey("venta.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_producto = Column(Float, nullable=False)

    producto = relationship("Producto")
    venta = relationship("Venta", back_populates="detalles")