from sqlalchemy import Column, Integer, String, Float, Date
from .base import Base

class Inversion(Base):
    __tablename__ = "inversiones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    saldo = Column(Float, nullable=False)
    fecha_vencimiento = Column(Date, nullable=False)
