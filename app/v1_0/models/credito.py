from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from .base import Base

class Credito(Base):
    __tablename__ = "credito"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    monto = Column(Float, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now)
