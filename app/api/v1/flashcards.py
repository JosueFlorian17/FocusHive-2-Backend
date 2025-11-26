from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
# Importamos modelos Pydantic y ORM
from app.models.pydantic_models import (
    CollectionCreate, CollectionOut, CollectionOutWithCards,
    FlashcardCreate, FlashcardOut, FlashcardBase
)
from app.models.orm_models import CardCollection, Flashcard
from app.models.user import Usuario

router = APIRouter(
    prefix="/flashcards",
    tags=["Flashcards y Colecciones"],
)

# --- Endpoints para COLECCIONES ---

@router.post("/collections", response_model=CollectionOut, status_code=status.HTTP_201_CREATED)
def create_collection(collection_data: CollectionCreate, db: Session = Depends(get_db)):
    """Crea una nueva colección de flashcards (global)."""
    
    # Convertimos el color hex string a bytes si es necesario, 
    # pero como usamos String(6) en ORM, lo pasamos directo.
    db_collection = CardCollection(
        collection_name=collection_data.collection_name,
        collection_color=collection_data.collection_color,
        is_active=collection_data.is_active
    )
    
    db.add(db_collection)
    db.commit()
    db.refresh(db_collection)
    return db_collection

@router.get("/collections", response_model=List[CollectionOut])
def get_all_collections(db: Session = Depends(get_db)):
    """Obtiene todas las colecciones (sin tarjetas)."""
    collections = db.query(CardCollection).filter(CardCollection.is_active == True).all()
    return collections

@router.get("/collections/{collection_id}", response_model=CollectionOutWithCards)
def get_collection_with_cards(collection_id: int, db: Session = Depends(get_db)):
    """Obtiene una colección específica y todas sus tarjetas."""
    collection = db.query(CardCollection).filter(CardCollection.collection_id == collection_id).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Colección no encontrada")
    return collection

@router.delete("/collections/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection(collection_id: int, db: Session = Depends(get_db)):
    """Elimina una colección (y sus tarjetas en cascada)."""
    db_collection = db.query(CardCollection).filter(CardCollection.collection_id == collection_id).first()
    if not db_collection:
        raise HTTPException(status_code=404, detail="Colección no encontrada")
    
    db.delete(db_collection)
    db.commit()
    return None # Retorna 204 No Content

# --- Endpoints para FLASHCARDS (dentro de una colección) ---

@router.post("/collections/{collection_id}/cards", response_model=FlashcardOut, status_code=status.HTTP_201_CREATED)
def create_flashcard_in_collection(
    collection_id: int, 
    card_data: FlashcardCreate, 
    db: Session = Depends(get_db)
):
    """Crea una nueva flashcard asociada a un usuario y una colección."""
    
    # 1. Verificar que la colección exista
    db_collection = db.query(CardCollection).filter(CardCollection.collection_id == collection_id).first()
    if not db_collection:
        raise HTTPException(status_code=404, detail="ID de Colección no encontrado")

    # 2. Verificar que el usuario exista
    db_user = db.query(Usuario).filter(Usuario.user_id == card_data.card_user).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="ID de Usuario no encontrado")

    # 3. Crear la flashcard
    db_card = Flashcard(
        **card_data.dict(), # Pasa question, answer, card_user, etc.
        collection=collection_id, # Asigna el ID de la colección
        is_active=True
    )
    
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card

@router.put("/cards/{card_id}", response_model=FlashcardOut)
def update_flashcard(card_id: int, card_data: FlashcardBase, db: Session = Depends(get_db)):
    """Actualiza el contenido de una flashcard (pregunta, respuesta, etc.)."""
    db_card = db.query(Flashcard).filter(Flashcard.card_id == card_id).first()
    if not db_card:
        raise HTTPException(status_code=404, detail="Flashcard no encontrada")

    update_dict = card_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(db_card, key, value)
        
    db.commit()
    db.refresh(db_card)
    return db_card

@router.delete("/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_flashcard(card_id: int, db: Session = Depends(get_db)):
    """Elimina una flashcard específica."""
    db_card = db.query(Flashcard).filter(Flashcard.card_id == card_id).first()
    if not db_card:
        raise HTTPException(status_code=404, detail="Flashcard no encontrada")
        
    db.delete(db_card)
    db.commit()
    return None