from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base

class DetallePagoCompra(Base):
    __tablename__ = "detalle_pago_compra"

    id = Column(Integer, primary_key=True, autoincrement=True)
    compra_id = Column(Integer, ForeignKey("compra.id"), nullable=False)
    banco_id = Column(Integer, ForeignKey("banco.id"), nullable=False)
    monto = Column(Float, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now, nullable=False)

    compra = relationship("Compra", back_populates="pagos_compra")
    banco  = relationship("Banco")
