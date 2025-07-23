from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class DetalleCompra(Base):
    __tablename__ = "detalle_compra"

    id = Column(Integer, primary_key=True, autoincrement=True)
    producto_id = Column(Integer, ForeignKey("producto.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    compra_id = Column(Integer, ForeignKey("compra.id"), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now)

    producto = relationship("Producto")
    compra = relationship("Compra", back_populates="detalles")
