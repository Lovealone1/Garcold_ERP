from sqlalchemy import Column, Integer, String
from .base import Base  

class Estado(Base):
    __tablename__ = "estado"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
