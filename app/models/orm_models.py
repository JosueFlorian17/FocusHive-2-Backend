from sqlalchemy import (
    Boolean, Column, Integer, String, ForeignKey, DATETIME, TEXT, func, UniqueConstraint
)
from sqlalchemy.orm import relationship
# Asegúrate de que ColorString esté importado correctamente desde db.py
from app.database.connection import Base, ColorString 



# --- 2. Tabla POSTS (SIN CAMBIOS ESTRUCTURALES) ---
class Post(Base):
    __tablename__ = "posts"

    post_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuario.user_id"), nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    image_url = Column(String(255), nullable=False, unique=True)
    description = Column(String(151), nullable=True)
    publish_date = Column(DATETIME, nullable=False)

    user = relationship("Usuario", back_populates="posts")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")

# --- 3. Tabla CARD_COLLECTIONS (SIN CAMBIOS ESTRUCTURALES) ---
class CardCollection(Base):
    __tablename__ = "card_collections"

    collection_id = Column(Integer, primary_key=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    collection_name = Column(String(50), nullable=False)
    collection_color = Column(ColorString, nullable=False) # Usa ColorString para VARBINARY

    flashcards = relationship("Flashcard", back_populates="collection_owner", cascade="all, delete-orphan")

# --- 4. Tabla FLASHCARDS (SIN CAMBIOS ESTRUCTURALES) ---
class Flashcard(Base):
    __tablename__ = "flashcards"

    card_id = Column(Integer, primary_key=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_reversed = Column(Boolean, default=False, nullable=False)
    card_user = Column(Integer, ForeignKey("usuario.user_id"), nullable=False)
    question = Column(String(55), nullable=False)
    answer = Column(String(255), nullable=False)
    collection = Column(Integer, ForeignKey("card_collections.collection_id"), nullable=False)
    flashcard_color = Column(String(45), nullable=True)

    collection_owner = relationship("CardCollection", back_populates="flashcards")
    user = relationship("Usuario", back_populates="flashcards")







# --- 8. Tabla LIKES (SIN CAMBIOS ESTRUCTURALES) ---
class Like(Base):
    __tablename__ = "likes"

    like_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuario.user_id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.post_id"), nullable=False)
    like_date = Column(DATETIME, nullable=False)
    __table_args__ = (UniqueConstraint('user_id', 'post_id', name='uq_user_post_like'),) # Restricción única
    
    user = relationship("Usuario", back_populates="likes")
    post = relationship("Post", back_populates="likes")

