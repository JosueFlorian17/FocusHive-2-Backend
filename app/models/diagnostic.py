from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base

class DiagnosticQuestion(Base):
    __tablename__ = "diagnostic_questions"
    
    question_id = Column(Integer, primary_key=True, autoincrement=True)
    question_text = Column(Text, nullable=False)
    question_order = Column(Integer, nullable=False)
    
    # Relationships
    options = relationship("DiagnosticOption", back_populates="question", cascade="all, delete-orphan")
    responses = relationship("DiagnosticResponse", back_populates="question", cascade="all, delete-orphan")

class DiagnosticOption(Base):
    __tablename__ = "diagnostic_options"
    
    option_id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey("diagnostic_questions.question_id"), nullable=False)
    option_text = Column(Text, nullable=False)
    method_id = Column(Integer, ForeignKey("metodos.metodo_id"), nullable=False)
    points = Column(Integer, default=1, nullable=False)
    
    # Relationships
    question = relationship("DiagnosticQuestion", back_populates="options")
    method = relationship("Metodo")
    responses = relationship("DiagnosticResponse", back_populates="option", cascade="all, delete-orphan")

class DiagnosticResponse(Base):
    __tablename__ = "diagnostic_responses"
    
    response_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("usuario.user_id"), nullable=False)
    question_id = Column(Integer, ForeignKey("diagnostic_questions.question_id"), nullable=False)
    option_id = Column(Integer, ForeignKey("diagnostic_options.option_id"), nullable=False)
    answered_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("Usuario")
    question = relationship("DiagnosticQuestion", back_populates="responses")
    option = relationship("DiagnosticOption", back_populates="responses")