from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc # Importar desc para ordenar
from app.database.connection import get_db
from typing import List # Importar List
# Importar el SessionCreate y SessionUpdate actualizados
from app.models.pydantic_models import SessionCreate, SessionUpdate, SessionOut
from app.models.study_session import SesionEstudio
from app.models.user import Usuario


router = APIRouter(
    prefix="/sessions",
    tags=["Sesiones de Estudio"],
)

# 1. Módulo de Inicio de Sesión de Estudio (POST /sessions)
@router.post("/", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def start_session(session_data: SessionCreate, db: Session = Depends(get_db)):
    """Registra el inicio de una nueva sesión de estudio."""
    
    # Verificación: ¿Existe el usuario?
    db_user = db.query(Usuario).filter(Usuario.user_id == session_data.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Creamos el objeto ORM, incluyendo el nuevo campo 'descripcion'
    db_session = SesionEstudio(
        user_id=session_data.user_id,
        metodo_id=session_data.metodo_id,
        fecha_inicio=session_data.fecha_inicio,
        duracion_minutos=0,
        fue_completada=False,
        descripcion=session_data.descripcion # <--- CAMBIO/ACTUALIZACIÓN
    )
    
    db.add(db_session)
    db.commit()
    db.refresh(db_session) # Obtenemos el session_id generado por la BD
    
    return db_session

# 2 & 3. Módulo de Pausado/Reanudado/Finalizado de Sesión (PUT /sessions/{id})
@router.put("/{session_id}", response_model=SessionOut)
def update_session(session_id: int, update_data: SessionUpdate, db: Session = Depends(get_db)):
    """Actualiza la sesión (pausar, reanudar, finalizar, o añadir descripción)."""
    
    db_session = db.query(SesionEstudio).filter(SesionEstudio.session_id == session_id).first()
    
    if not db_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesión no encontrada")

    # Actualizamos solo los campos que vienen en el body (incluye duracion_minutos, fue_completada, y descripcion)
    # Nota: El pydantic SessionUpdate ya incluye 'descripcion: Optional[str] = None'
    update_dict = update_data.dict(exclude_unset=True)
    
    for key, value in update_dict.items():
        setattr(db_session, key, value)
    
    # Lógica para actualizar el tiempo total estudiado del usuario si la sesión fue completada
    if update_data.fue_completada and update_data.duracion_minutos:
        db_user = db.query(Usuario).filter(Usuario.user_id == db_session.user_id).first()
        if db_user:
            db_user.total_studied_time += update_data.duracion_minutos

    db.commit()
    db.refresh(db_session)
    
    return db_session


# Endpoint para obtener el historial de sesiones de un usuario
@router.get("/users/{user_id}/sessions", response_model=List[SessionOut])
def get_user_sessions(user_id: int, db: Session = Depends(get_db)):
    """Obtiene el historial completo de sesiones de estudio para un usuario."""
    
    # Verificación: ¿Existe el usuario?
    db_user = db.query(Usuario).filter(Usuario.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Obtenemos las sesiones del usuario, ordenadas por fecha de inicio descendente
    sessions = db.query(SesionEstudio).filter(SesionEstudio.user_id == user_id).order_by(desc(SesionEstudio.fecha_inicio)).all()
    
    return sessions