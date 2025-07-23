from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base  # si tienes Base en un módulo común

class Venta(Base):
    __tablename__ = "venta"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey("cliente.id"), nullable=False)
    banco_id = Column(Integer, ForeignKey("banco.id"), nullable=False)
    total = Column(Float, nullable=False)
    estado_id = Column(Integer, nullable=False)
    saldo_restante = Column(Float, nullable=True)
    fecha = Column(DateTime, default=datetime.now)

    cliente = relationship("Cliente")
    banco = relationship("Banco")
    detalles = relationship("DetalleVenta", back_populates="venta", cascade="all, delete-orphan")
