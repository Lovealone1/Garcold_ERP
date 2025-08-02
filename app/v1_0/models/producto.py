# producto.py
from sqlalchemy import Column, Integer, String, Float,DateTime, Boolean
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime
class Producto(Base):
    __tablename__ = "producto"

    id = Column(Integer, primary_key=True, autoincrement=True)
    referencia = Column(String(50), unique=True, nullable=False)
    descripcion = Column(String(255), nullable=False)
    precio_compra = Column(Float, nullable=False)
    precio_venta = Column(Float, nullable=False)
    cantidad = Column(Integer, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now)

    detalles_venta = relationship("DetalleVenta", back_populates="producto", cascade="all, delete-orphan")
