from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Cliente(Base):
    __tablename__ = "cliente"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cc_nit = Column(String, nullable=False, unique=True)
    nombre = Column(String, nullable=False)
    direccion = Column(String, nullable=False)
    ciudad = Column(String, nullable=False)
    celular = Column(String, nullable=True)
    correo = Column(String, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.now)
    saldo = Column(Float, default=0.0)
