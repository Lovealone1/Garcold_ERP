from sqlalchemy import Column, Integer, String
from .base import Base

class TipoTransaccion(Base):
    __tablename__ = "tipo_transacciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)