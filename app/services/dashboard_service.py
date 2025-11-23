from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status
from typing import List, Dict, Optional
from datetime import datetime

from app.models.study_session import SesionEstudio
from app.models.user import Usuario
from app.models.method import Metodo
from app.models.user_method import UsuarioMetodo
from app.schemas.dashboard import CreateStudySessionSchema
from app.utils.dashboard_utils import DashboardCalculator

class DashboardService:
    """Servicio para gestionar el dashboard y sesiones de estudio"""
    
    @staticmethod
    def create_study_session(
        db: Session,
        user_id: int,
        session_data: CreateStudySessionSchema
    ) -> SesionEstudio:
        """
        Crea una nueva sesión de estudio.
        Implementa parte del requisito funcional #2 (almacenar métricas de sesiones)
        """
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
            # Crear sesión
            new_session = SesionEstudio(
                user_id=user_id,
                metodo_id=session_data.metodo_id,
                fecha_inicio=session_data.fecha_inicio,
                duracion_minutos=session_data.duracion_minutos,
                fue_completada=session_data.fue_completada,
                descripcion=session_data.descripcion
            )
            
            db.add(new_session)
            
            # Actualizar total_studied_time del usuario
            user = db.query(Usuario).filter(Usuario.user_id == user_id).first()
            user.total_studied_time += session_data.duracion_minutos
            
            # Marcar método como utilizado en usuario_metodo
            user_method = db.query(UsuarioMetodo).filter(
                UsuarioMetodo.user_id == user_id,
                UsuarioMetodo.metodo_id == session_data.metodo_id
            ).first()
            
            if user_method:
                user_method.es_utilizado = True
            else:
                new_user_method = UsuarioMetodo(
                    user_id=user_id,
                    metodo_id=session_data.metodo_id,
                    es_recomendado=False,
                    es_utilizado=True
                )
                db.add(new_user_method)
            
            db.commit()
            db.refresh(new_session)
            
            return new_session
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear la sesión: {str(e)}"
            )
    
    @staticmethod
    def get_dashboard_summary(db: Session, user_id: int) -> Dict:
        """
        Obtiene el resumen completo del dashboard.
        Implementa el requisito funcional #3 y #4 (visualizar dashboard con métricas)
        """
        # Obtener usuario
        user = db.query(Usuario).filter(Usuario.user_id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Rangos de fechas
        today_start, today_end = DashboardCalculator.get_date_range('today')
        week_start, week_end = DashboardCalculator.get_date_range('week')
        
        # Métricas de hoy
        today_minutes = DashboardCalculator.calculate_total_minutes(db, user_id, today_start, today_end)
        today_sessions = DashboardCalculator.calculate_session_count(db, user_id, today_start, today_end)
        
        # Métricas de la semana
        week_minutes = DashboardCalculator.calculate_total_minutes(db, user_id, week_start, week_end)
        week_hours = round(week_minutes / 60, 2)
        
        # Método recomendado
        recommended_method_data = db.query(UsuarioMetodo, Metodo).join(
            Metodo, UsuarioMetodo.metodo_id == Metodo.metodo_id
        ).filter(
            UsuarioMetodo.user_id == user_id,
            UsuarioMetodo.es_recomendado == True
        ).first()
        
        recommended_method = None
        if recommended_method_data:
            method = recommended_method_data[1]
            method_usage = DashboardCalculator.get_method_usage(db, user_id)
            method_stats = next((m for m in method_usage if m['metodo_id'] == method.metodo_id), None)
            
            if method_stats:
                recommended_method = method_stats
            else:
                recommended_method = {
                    "metodo_id": method.metodo_id,
                    "metodo_nombre": method.nombre,
                    "total_sessions": 0,
                    "total_minutes": 0,
                    "total_hours": 0.0,
                    "percentage": 0.0
                }
        
        # Método más usado
        methods_usage = DashboardCalculator.get_method_usage(db, user_id)
        most_used_method = methods_usage[0] if methods_usage else None
        
        # Racha de estudio
        study_streak = DashboardCalculator.calculate_study_streak(db, user_id)
        
        # Progreso semanal
        daily_breakdown = DashboardCalculator.get_daily_breakdown(db, user_id, week_start, week_end)
        
        return {
            "user_id": user.user_id,
            "username": user.username,
            "level": user.level,
            "total_studied_time": user.total_studied_time,
            "today_minutes": today_minutes,
            "today_sessions": today_sessions,
            "week_minutes": week_minutes,
            "week_hours": week_hours,
            "recommended_method": recommended_method,
            "most_used_method": most_used_method,
            "study_streak": study_streak,
            "weekly_progress": {
                "week_start": week_start.date(),
                "week_end": week_end.date(),
                "total_minutes": week_minutes,
                "total_hours": week_hours,
                "total_sessions": DashboardCalculator.calculate_session_count(db, user_id, week_start, week_end),
                "completed_sessions": DashboardCalculator.calculate_session_count(db, user_id, week_start, week_end, completed_only=True),
                "daily_breakdown": daily_breakdown
            },
            "methods_usage": methods_usage
        }
    
    @staticmethod
    def get_session_history(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> Dict:
        """Obtiene el historial de sesiones de estudio paginado"""
        # Total de sesiones
        total = db.query(SesionEstudio).filter(
            SesionEstudio.user_id == user_id
        ).count()
        
        # Sesiones paginadas (más recientes primero)
        sessions = db.query(SesionEstudio).filter(
            SesionEstudio.user_id == user_id
        ).order_by(
            desc(SesionEstudio.fecha_inicio)
        ).offset(skip).limit(limit).all()
        
        # Obtener nombres de métodos
        sessions_with_method = []
        for session in sessions:
            method = db.query(Metodo).filter(
                Metodo.metodo_id == session.metodo_id
            ).first()
            
            sessions_with_method.append({
                "session_id": session.session_id,
                "user_id": session.user_id,
                "metodo_id": session.metodo_id,
                "metodo_nombre": method.nombre if method else "Desconocido",
                "fecha_inicio": session.fecha_inicio,
                "duracion_minutos": session.duracion_minutos,
                "fue_completada": session.fue_completada,
                "descripcion": session.descripcion
            })
        
        return {
            "sessions": sessions_with_method,
            "total_count": total,
            "page": (skip // limit) + 1,
            "pages": (total + limit - 1) // limit
        }
    
    @staticmethod
    def get_monthly_stats(db: Session, user_id: int, month: int, year: int) -> Dict:
        """Obtiene estadísticas mensuales"""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year, 12, 31, 23, 59, 59)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        total_minutes = DashboardCalculator.calculate_total_minutes(db, user_id, start_date, end_date)
        total_sessions = DashboardCalculator.calculate_session_count(db, user_id, start_date, end_date)
        
        average_duration = round(total_minutes / total_sessions, 2) if total_sessions > 0 else 0
        most_productive_day = DashboardCalculator.get_most_productive_day(db, user_id, month, year)
        
        return {
            "month": month,
            "year": year,
            "total_minutes": total_minutes,
            "total_hours": round(total_minutes / 60, 2),
            "total_sessions": total_sessions,
            "average_session_duration": average_duration,
            "most_productive_day": most_productive_day
        }