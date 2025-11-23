from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Metodo(Base):
    __tablename__ = "metodos"
    
    metodo_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(45), unique=True, nullable=False, index=True)
    descripcion = Column(Text, nullable=False)
    tipo_aprendizaje_compatible = Column(String(45), nullable=False)
    
    def __repr__(self):
        return f"<Metodo(id={self.metodo_id}, nombre='{self.nombre}')>"