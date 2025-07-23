from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Producto(Base):
    __tablename__ = "producto"

    id = Column(Integer, primary_key=True, autoincrement=True)
    referencia = Column(String, nullable=False, unique=True)
    descripcion = Column(String, nullable=False)
    cantidad = Column(Integer, nullable=True, default=0)
    precio_compra = Column(Float, nullable=False)
    precio_venta = Column(Float, nullable=False)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.now)
