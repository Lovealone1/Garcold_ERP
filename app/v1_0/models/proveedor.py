from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .base import Base

class Proveedor(Base):
    __tablename__ = "proveedor"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cc_nit = Column(String, nullable=False, unique=True)
    nombre = Column(String, nullable=False)
    direccion = Column(String, nullable=False)
    ciudad = Column(String, nullable=False)
    celular = Column(String, nullable=True)
    correo = Column(String, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.now)
