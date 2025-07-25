from sqlalchemy import Column, Integer, String
from app.v1_0.models.base import Base

class CategoriaGastos(Base):
    __tablename__ = "categoria_gastos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
