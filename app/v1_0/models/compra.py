from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Compra(Base):
    __tablename__ = "compra"

    id = Column(Integer, primary_key=True, autoincrement=True)
    proveedor_id = Column(Integer, ForeignKey("proveedor.id"), nullable=False)
    total = Column(Float, nullable=False)
    banco_id = Column(Integer, ForeignKey("banco.id"), nullable=False)
    estado_id = Column(Integer, nullable=False)
    saldo = Column(Float, nullable=True)
    fecha_compra = Column(DateTime, default=datetime.now)

    proveedor = relationship("Proveedor")
    banco = relationship("Banco")
    detalles = relationship("DetalleCompra", back_populates="compra", cascade="all, delete-orphan")
    pagos_compra = relationship(
        "DetallePagoCompra",
        back_populates="compra"
    )