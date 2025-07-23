from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Utilidad(Base):
    __tablename__ = "utilidades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    venta_id = Column(Integer, ForeignKey("venta.id"), nullable=False)
    utilidad = Column(Float, nullable=False)
    fecha = Column(DateTime, default=datetime.now)

    venta = relationship("Venta")
    detalles = relationship("DetalleUtilidad", back_populates="utilidad", cascade="all, delete-orphan")
