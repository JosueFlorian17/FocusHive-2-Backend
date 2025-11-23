from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from datetime import datetime, date
from enum import Enum

# ===== ENUMS =====
class DayOfWeek(str, Enum):
    """Días de la semana"""
    LUNES = "lunes"
    MARTES = "martes"
    MIERCOLES = "miercoles"
    JUEVES = "jueves"
    VIERNES = "viernes"
    SABADO = "sabado"
    DOMINGO = "domingo"

# ===== CREATE SESSION SCHEMAS =====
class CreateStudySessionSchema(BaseModel):
    """Schema para crear una nueva sesión de estudio"""
    metodo_id: int = Field(..., gt=0, description="ID del método de estudio utilizado")
    fecha_inicio: datetime = Field(..., description="Fecha y hora de inicio de la sesión")
    duracion_minutos: int = Field(..., gt=0, le=1440, description="Duración en minutos (máximo 24 horas)")
    fue_completada: bool = Field(True, description="Si la sesión fue completada o interrumpida")
    descripcion: Optional[str] = Field(None, max_length=500, description="Descripción opcional de la sesión")
    
    @validator('duracion_minutos')
    def validate_duration(cls, v):
        if v <= 0:
            raise ValueError('La duración debe ser mayor a 0 minutos')
        if v > 1440:  # 24 horas
            raise ValueError('La duración no puede ser mayor a 24 horas (1440 minutos)')
        return v
    
    @validator('fecha_inicio')
    def validate_date(cls, v):
        if v > datetime.now():
            raise ValueError('La fecha de inicio no puede ser en el futuro')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "metodo_id": 1,
                "fecha_inicio": "2025-01-20T14:30:00",
                "duracion_minutos": 50,
                "fue_completada": True,
                "descripcion": "Sesión de estudio de matemáticas usando Pomodoro"
            }
        }


class StudySessionResponse(BaseModel):
    """Schema de respuesta para una sesión de estudio"""
    session_id: int
    user_id: int
    metodo_id: int
    metodo_nombre: str
    fecha_inicio: datetime
    duracion_minutos: int
    fue_completada: bool
    descripcion: Optional[str]
    
    class Config:
        from_attributes = True

class CreateSessionResponse(BaseModel):
    """Schema de respuesta al crear una sesión"""
    message: str
    session: StudySessionResponse


class DailyProgressSchema(BaseModel):
    """Progreso diario"""
    date: date
    total_minutes: int
    total_sessions: int
    completed_sessions: int
    completion_rate: float  # Porcentaje

class WeeklyProgressSchema(BaseModel):
    """Progreso semanal"""
    week_start: date
    week_end: date
    total_minutes: int
    total_hours: float
    total_sessions: int
    completed_sessions: int
    daily_breakdown: List[DailyProgressSchema]

class MethodUsageSchema(BaseModel):
    """Uso de métodos de estudio"""
    metodo_id: int
    metodo_nombre: str
    total_sessions: int
    total_minutes: int
    total_hours: float
    percentage: float  # Porcentaje de uso respecto al total

class StudyStreakSchema(BaseModel):
    """Racha de estudio"""
    current_streak: int  # Días consecutivos estudiando
    longest_streak: int  # Racha más larga
    last_study_date: Optional[date]

class SessionHistorySchema(BaseModel):
    """Historial de sesiones"""
    sessions: List[StudySessionResponse]
    total_count: int
    page: int
    pages: int

class DashboardSummarySchema(BaseModel):
    """Resumen completo del dashboard"""
    # Datos del usuario
    user_id: int
    username: str
    level: int
    total_studied_time: int  # Total de minutos históricos
    
    # Progreso actual
    today_minutes: int
    today_sessions: int
    week_minutes: int
    week_hours: float
    
    # Método recomendado y más usado
    recommended_method: Optional[MethodUsageSchema]
    most_used_method: Optional[MethodUsageSchema]
    
    # Racha
    study_streak: StudyStreakSchema
    
    # Progreso semanal
    weekly_progress: WeeklyProgressSchema
    
    # Todos los métodos usados
    methods_usage: List[MethodUsageSchema]


class MonthlyStatsSchema(BaseModel):
    """Estadísticas mensuales"""
    month: int
    year: int
    total_minutes: int
    total_hours: float
    total_sessions: int
    average_session_duration: float
    most_productive_day: Optional[str]

class YearlyStatsSchema(BaseModel):
    """Estadísticas anuales"""
    year: int
    total_minutes: int
    total_hours: float
    total_sessions: int
    monthly_breakdown: List[MonthlyStatsSchema]