# app/models/study.py (Código Corregido)

from pydantic import BaseModel
from datetime import datetime
# >> IMPORTAR Optional <<
from typing import Optional 

# -----------------------------------------------------
# Para Sesiones de Estudio
# -----------------------------------------------------

class SessionCreate(BaseModel):
    user_id: int
    metodo_id: int
    fecha_inicio: datetime = datetime.now() # Valor por defecto

class SessionUpdate(BaseModel):
    # Usado para Pausar, Reanudar o Finalizar
    # ANTES: duracion_minutos: int | None = None
    # DESPUÉS:
    duracion_minutos: Optional[int] = None
    # ANTES: fue_completada: bool | None = None
    # DESPUÉS:
    fue_completada: Optional[bool] = None

class SessionOut(BaseModel):
    session_id: int
    user_id: int
    metodo_id: int
    fecha_inicio: datetime
    duracion_minutos: int
    fue_completada: bool

    class Config:
        from_attributes = True