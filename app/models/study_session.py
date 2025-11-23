from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base

class SesionEstudio(Base):
    __tablename__ = "sesion_estudio"
    
    session_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("usuario.user_id"), nullable=False)
    metodo_id = Column(Integer, ForeignKey("metodos.metodo_id"), nullable=False)
    fecha_inicio = Column(DateTime(timezone=True), nullable=False)
    duracion_minutos = Column(Integer, nullable=False)
    fue_completada = Column(Boolean, nullable=False)
    descripcion = Column(Text, nullable=True)  # Campo adicional para descripción
    
    # Relationships
    user = relationship("Usuario", foreign_keys=[user_id])
    method = relationship("Metodo", foreign_keys=[metodo_id])
    
    def __repr__(self):
        return f"<SesionEstudio(id={self.session_id}, user_id={self.user_id}, duracion={self.duracion_minutos}min)>"