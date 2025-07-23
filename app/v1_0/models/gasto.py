from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Gasto(Base):
    __tablename__ = "gastos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    categoria_gasto_id = Column(Integer, ForeignKey("categoria_gastos.id"), nullable=False)
    monto = Column(Float, nullable=False)
    banco_id = Column(Integer, ForeignKey("banco.id"), nullable=False)
    fecha_gasto = Column(Date, nullable=False)

    banco = relationship("Banco")
    categoria = relationship("CategoriaGastos")
