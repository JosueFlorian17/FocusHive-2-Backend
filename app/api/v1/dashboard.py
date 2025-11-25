from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from app.database.connection import get_db
from app.api.dependencies import get_current_user
from app.models.user import Usuario
from app.schemas.dashboard import (
    CreateStudySessionSchema,
    CreateSessionResponse,
    StudySessionResponse,
    DashboardSummarySchema,
    SessionHistorySchema,
    MonthlyStatsSchema
)
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# CREATE SESSION 
@router.post(
    "/sessions",
    response_model=CreateSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear sesión de estudio",
    description="Registra una nueva sesión de estudio (Req. Funcional #2)"
)
async def create_study_session(
    session_data: CreateStudySessionSchema,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crea una nueva sesión de estudio y actualiza las métricas del usuario.
    
    
    Requiere: Token de autenticación
    
    Body Parameters:
        - metodo_id: ID del método de estudio utilizado
        - fecha_inicio: Fecha y hora de inicio de la sesión
        - duracion_minutos: Duración en minutos (1-1440)
        - fue_completada: Si la sesión fue completada
        - descripcion: Descripción opcional de la sesión
    
    Acciones realizadas:
        - Guarda la sesión en la base de datos
        - Actualiza total_studied_time del usuario
        - Marca el método como "utilizado" en usuario_metodo
    

```
    """
    new_session = DashboardService.create_study_session(db, current_user.user_id, session_data)
    
    return CreateSessionResponse(
        message="Sesión de estudio registrada exitosamente",
        session=StudySessionResponse(
            session_id=new_session.session_id,
            user_id=new_session.user_id,
            metodo_id=new_session.metodo_id,
            metodo_nombre=new_session.method.nombre,
            fecha_inicio=new_session.fecha_inicio,
            duracion_minutos=new_session.duracion_minutos,
            fue_completada=new_session.fue_completada,
            descripcion=new_session.descripcion
        )
    )

#  GET DASHBOARD SUMMARY
@router.get(
    "/summary",
    response_model=DashboardSummarySchema,
    summary="Obtener resumen del dashboard",
    description="Obtiene todas las métricas del dashboard (Req. Funcional #3 y #4)"
)
async def get_dashboard_summary(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene el resumen completo del dashboard con todas las métricas.
    
    Implementa los requisitos funcionales #3 y #4:
        - Visualizar dashboard con información de sesiones previas
        - Ver resultado del diagnóstico y método recomendado
    
    Requiere: Token de autenticación
    
    Retorna:
        - Datos del usuario (level, total_studied_time)
        - Progreso de hoy (minutos y sesiones)
        - Progreso semanal (minutos, horas, sesiones)
        - Método recomendado (del diagnóstico)
        - Método más usado
        - Racha de estudio (días consecutivos)
        - Desglose diario de la semana
        - Uso de todos los métodos (con porcentajes)
    
    Ejemplo de uso en el frontend:
        - Mostrar "Hoy estudiaste X minutos en Y sesiones"
        - Gráfico de progreso semanal
        - Badge con racha actual
        - Lista de métodos más usados
    """
    summary = DashboardService.get_dashboard_summary(db, current_user.user_id)
    return summary

# GET SESSION HISTORY
@router.get(
    "/sessions/history",
    response_model=SessionHistorySchema,
    summary="Obtener historial de sesiones",
    description="Obtiene el historial paginado de sesiones de estudio"
)
async def get_session_history(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de registros"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial de sesiones de estudio ordenado por fecha (más recientes primero).
    
    Requiere: Token de autenticación
    
    Query Parameters:
        - skip: Para paginación (default: 0)
        - limit: Cantidad de registros (default: 20, max: 100)
    
    Retorna:
        - sessions: Lista de sesiones con toda la información
        - total_count: Total de sesiones del usuario
        - page: Página actual
        - pages: Total de páginas
    
    Cada sesión incluye:
        - ID, fecha, duración, método usado
        - Si fue completada o no
        - Descripción (si existe)
    """
    history = DashboardService.get_session_history(db, current_user.user_id, skip, limit)
    return history

#  GET SESSION BY ID 
@router.get(
    "/sessions/{session_id}",
    response_model=StudySessionResponse,
    summary="Obtener sesión específica",
    description="Obtiene los detalles de una sesión de estudio específica"
)
async def get_session_by_id(
    session_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene los detalles de una sesión de estudio específica.
    
    Requiere: Token de autenticación
    
    Path Parameters:
        - session_id: ID de la sesión
    
    Solo puede acceder el usuario dueño de la sesión.
    """
    from app.models.study_session import SesionEstudio
    from fastapi import HTTPException
    
    session = db.query(SesionEstudio).filter(
        SesionEstudio.session_id == session_id,
        SesionEstudio.user_id == current_user.user_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión no encontrada"
        )
    
    return StudySessionResponse(
        session_id=session.session_id,
        user_id=session.user_id,
        metodo_id=session.metodo_id,
        metodo_nombre=session.method.nombre,
        fecha_inicio=session.fecha_inicio,
        duracion_minutos=session.duracion_minutos,
        fue_completada=session.fue_completada,
        descripcion=session.descripcion
    )

# UPDATE SESSION
@router.put(
    "/sessions/{session_id}",
    response_model=StudySessionResponse,
    summary="Actualizar sesión de estudio",
    description="Actualiza los datos de una sesión de estudio existente"
)
async def update_study_session(
    session_id: int,
    session_data: CreateStudySessionSchema,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza una sesión de estudio existente.
    
    Requiere: Token de autenticación
    
    Path Parameters:
        - session_id: ID de la sesión a actualizar
    
    Body: Mismos campos que al crear una sesión
    
    Nota: También actualiza el total_studied_time del usuario.
    """
    from app.models.study_session import SesionEstudio
    from app.models.method import Metodo
    from fastapi import HTTPException
    
    # Verificar que la sesión existe y pertenece al usuario
    session = db.query(SesionEstudio).filter(
        SesionEstudio.session_id == session_id,
        SesionEstudio.user_id == current_user.user_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión no encontrada"
        )
    
    # Verificar que el método existe
    method = db.query(Metodo).filter(
        Metodo.metodo_id == session_data.metodo_id
    ).first()
    
    if not method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Método con ID {session_data.metodo_id} no encontrado"
        )
    
    try:
        # Calcular diferencia de duración para actualizar total_studied_time
        old_duration = session.duracion_minutos
        new_duration = session_data.duracion_minutos
        duration_diff = new_duration - old_duration
        
        # Actualizar sesión
        session.metodo_id = session_data.metodo_id
        session.fecha_inicio = session_data.fecha_inicio
        session.duracion_minutos = session_data.duracion_minutos
        session.fue_completada = session_data.fue_completada
        session.descripcion = session_data.descripcion
        
        # Actualizar total_studied_time del usuario
        user = db.query(Usuario).filter(Usuario.user_id == current_user.user_id).first()
        user.total_studied_time += duration_diff
        
        db.commit()
        db.refresh(session)
        
        return StudySessionResponse(
            session_id=session.session_id,
            user_id=session.user_id,
            metodo_id=session.metodo_id,
            metodo_nombre=method.nombre,
            fecha_inicio=session.fecha_inicio,
            duracion_minutos=session.duracion_minutos,
            fue_completada=session.fue_completada,
            descripcion=session.descripcion
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar la sesión: {str(e)}"
        )

#  DELETE SESSION 
@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar sesión de estudio",
    description="Elimina una sesión de estudio"
)
async def delete_study_session(
    session_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Elimina una sesión de estudio.
    
    Requiere: Token de autenticación
    
    Path Parameters:
        - session_id: ID de la sesión a eliminar
    
    Nota: También actualiza el total_studied_time del usuario restando los minutos.
    """
    from app.models.study_session import SesionEstudio
    from fastapi import HTTPException
    
    session = db.query(SesionEstudio).filter(
        SesionEstudio.session_id == session_id,
        SesionEstudio.user_id == current_user.user_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión no encontrada"
        )
    
    try:
        # Actualizar total_studied_time del usuario
        user = db.query(Usuario).filter(Usuario.user_id == current_user.user_id).first()
        user.total_studied_time -= session.duracion_minutos
        
        # Si total_studied_time queda negativo, ponerlo en 0
        if user.total_studied_time < 0:
            user.total_studied_time = 0
        
        db.delete(session)
        db.commit()
        
        return {
            "message": "Sesión eliminada exitosamente",
            "session_id": session_id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar la sesión: {str(e)}"
        )

#  GET MONTHLY STATS
@router.get(
    "/stats/monthly",
    response_model=MonthlyStatsSchema,
    summary="Obtener estadísticas mensuales",
    description="Obtiene estadísticas de estudio de un mes específico"
)
async def get_monthly_stats(
    month: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    year: int = Query(..., ge=2020, le=2100, description="Año"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas de estudio de un mes específico.
    
    Requiere: Token de autenticación
    
    Query Parameters:
        - month: Mes (1-12)
        - year: Año
    
    Retorna:
        - Total de minutos y horas estudiadas
        - Total de sesiones
        - Duración promedio por sesión
        - Día de la semana más productivo
    
    Ejemplo: GET /dashboard/stats/monthly?month=1&year=2025
    """
    stats = DashboardService.get_monthly_stats(db, current_user.user_id, month, year)
    return stats

# GET TODAY'S PROGRESS 
@router.get(
    "/progress/today",
    summary="Obtener progreso de hoy",
    description="Obtiene el resumen rápido del progreso de hoy"
)
async def get_today_progress(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene un resumen rápido del progreso de hoy.
    
    Requiere: Token de autenticación
    
    Retorna:
        - Total de minutos estudiados hoy
        - Total de sesiones hoy
        - Sesiones completadas hoy
        - Tasa de completitud
    
    Útil para widgets o notificaciones rápidas.
    """
    from app.utils.dashboard_utils import DashboardCalculator
    
    today_start, today_end = DashboardCalculator.get_date_range('today')
    
    total_minutes = DashboardCalculator.calculate_total_minutes(db, current_user.user_id, today_start, today_end)
    total_sessions = DashboardCalculator.calculate_session_count(db, current_user.user_id, today_start, today_end)
    completed_sessions = DashboardCalculator.calculate_session_count(db, current_user.user_id, today_start, today_end, completed_only=True)
    completion_rate = DashboardCalculator.calculate_completion_rate(db, current_user.user_id, today_start, today_end)
    
    return {
        "date": today_start.date(),
        "total_minutes": total_minutes,
        "total_hours": round(total_minutes / 60, 2),
        "total_sessions": total_sessions,
        "completed_sessions": completed_sessions,
        "completion_rate": completion_rate
    }

# GET WEEKLY PROGRESS 
@router.get(
    "/progress/weekly",
    summary="Obtener progreso semanal",
    description="Obtiene el progreso semanal con desglose diario"
)
async def get_weekly_progress(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene el progreso de la semana actual con desglose día por día.
    
    Requiere: Token de autenticación
    
    Retorna:
        - Total semanal (minutos, horas, sesiones)
        - Desglose diario (lunes a domingo)
        - Cada día incluye: minutos, sesiones, tasa de completitud
    
    Útil para gráficos de barras o líneas semanales.
    """
    from app.utils.dashboard_utils import DashboardCalculator
    
    week_start, week_end = DashboardCalculator.get_date_range('week')
    
    week_minutes = DashboardCalculator.calculate_total_minutes(db, current_user.user_id, week_start, week_end)
    week_sessions = DashboardCalculator.calculate_session_count(db, current_user.user_id, week_start, week_end)
    completed_sessions = DashboardCalculator.calculate_session_count(db, current_user.user_id, week_start, week_end, completed_only=True)
    daily_breakdown = DashboardCalculator.get_daily_breakdown(db, current_user.user_id, week_start, week_end)
    
    return {
        "week_start": week_start.date(),
        "week_end": week_end.date(),
        "total_minutes": week_minutes,
        "total_hours": round(week_minutes / 60, 2),
        "total_sessions": week_sessions,
        "completed_sessions": completed_sessions,
        "daily_breakdown": daily_breakdown
    }

#  GET METHOD STATISTICS
@router.get(
    "/stats/methods",
    summary="Obtener estadísticas de métodos",
    description="Obtiene estadísticas de uso de todos los métodos de estudio"
)
async def get_method_statistics(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas de uso de todos los métodos de estudio.
    
    Requiere: Token de autenticación
    
    Retorna:
        - Lista de métodos ordenados por uso (más usado primero)
        - Para cada método:
            - Total de sesiones
            - Total de minutos y horas
            - Porcentaje de uso
    
    Útil para gráficos de torta o barras horizontales.
    """
    from app.utils.dashboard_utils import DashboardCalculator
    
    methods_usage = DashboardCalculator.get_method_usage(db, current_user.user_id)
    
    return {
        "methods": methods_usage,
        "total_methods_used": len(methods_usage)
    }