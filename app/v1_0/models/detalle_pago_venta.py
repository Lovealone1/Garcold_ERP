from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base

class DetallePagoVenta(Base):
    __tablename__ = "detalle_pago_venta"

    id = Column(Integer, primary_key=True, autoincrement=True)
    venta_id = Column(Integer, ForeignKey("venta.id"), nullable=False)
    banco_id = Column(Integer, ForeignKey("banco.id"), nullable=False)
    monto = Column(Float, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now, nullable=False)

    venta = relationship("Venta", back_populates="pagos_venta",)
    banco = relationship("Banco")
