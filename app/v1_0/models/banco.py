from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from .base import Base  

class Banco(Base):
    __tablename__ = "banco"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    saldo = Column(Float, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, nullable=True)
