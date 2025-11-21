from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.sql import func
from app.database.connection import Base

class Usuario(Base):
    __tablename__="usuario"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(45), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  
    email = Column(String(100), unique=True, nullable=False)  
    is_premium = Column(Boolean, default=False)
    level = Column(Integer, default=1, nullable=False)
    total_studied_time = Column(Integer, default=0, nullable=False)

    # Campos adicionales para el perfil
    full_name = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


    def __repr__(self):
        return f"<Usuario(user_id={self.user_id}, username='{self.username}')>"

