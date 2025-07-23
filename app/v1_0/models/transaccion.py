from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Transaccion(Base):
    __tablename__ = "transacciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    banco_id = Column(Integer, ForeignKey("banco.id"), nullable=False)
    monto = Column(Float, nullable=False)
    tipo_id = Column(Integer, ForeignKey("tipo_transacciones.id"), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now)

    banco = relationship("Banco")
    tipo = relationship("TipoTransaccion")
