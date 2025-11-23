from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database.connection import Base

class UsuarioMetodo(Base):
    __tablename__ = "usuario_metodo"
    
    user_id = Column(Integer, ForeignKey("usuario.user_id"), primary_key=True)
    metodo_id = Column(Integer, ForeignKey("metodos.metodo_id"), primary_key=True)
    es_recomendado = Column(Boolean, default=False, nullable=False)
    es_utilizado = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user = relationship("Usuario")
    method = relationship("Metodo")