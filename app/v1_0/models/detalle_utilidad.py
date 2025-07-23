from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class DetalleUtilidad(Base):
    __tablename__ = "detalle_utilidades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    venta_id = Column(Integer, ForeignKey("venta.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("producto.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_compra = Column(Float, nullable=False)
    precio_venta = Column(Float, nullable=False)
    total_utilidad = Column(Float, nullable=False)
    utilidad_id = Column(Integer, ForeignKey("utilidades.id"), nullable=True)

    venta = relationship("Venta")
    producto = relationship("Producto")
    utilidad = relationship("Utilidad", back_populates="detalles")
