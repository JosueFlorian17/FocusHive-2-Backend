from datetime import datetime, timedelta, date
from typing import List, Dict, Optional, Tuple
from sqlalchemy import func, extract, and_
from sqlalchemy.orm import Session
from app.models.study_session import SesionEstudio
from app.models.method import Metodo

class DashboardCalculator:
    """Utilidades para calcular métricas del dashboard"""
    
    @staticmethod
    def get_date_range(period: str = 'week') -> Tuple[datetime, datetime]:
        """
        Obtiene el rango de fechas según el período.
        
        Args:
            period: 'today', 'week', 'month', 'year'
        
        Returns:
            (fecha_inicio, fecha_fin)
        """
        now = datetime.now()
        
        if period == 'today':
            start = datetime(now.year, now.month, now.day, 0, 0, 0)
            end = datetime(now.year, now.month, now.day, 23, 59, 59)
        
        elif period == 'week':
            # Inicio de la semana (lunes)
            start = now - timedelta(days=now.weekday())
            start = datetime(start.year, start.month, start.day, 0, 0, 0)
            # Fin de la semana (domingo)
            end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
        elif period == 'month':
            start = datetime(now.year, now.month, 1, 0, 0, 0)
            # Último día del mes
            if now.month == 12:
                end = datetime(now.year, 12, 31, 23, 59, 59)
            else:
                end = datetime(now.year, now.month + 1, 1, 0, 0, 0) - timedelta(seconds=1)
        
        elif period == 'year':
            start = datetime(now.year, 1, 1, 0, 0, 0)
            end = datetime(now.year, 12, 31, 23, 59, 59)
        
        else:
            start = now
            end = now
        
        return start, end
    
    @staticmethod
    def calculate_total_minutes(db: Session, user_id: int, start_date: datetime, end_date: datetime) -> int:
        """Calcula el total de minutos estudiados en un período"""
        result = db.query(func.sum(SesionEstudio.duracion_minutos)).filter(
            SesionEstudio.user_id == user_id,
            SesionEstudio.fecha_inicio >= start_date,
            SesionEstudio.fecha_inicio <= end_date
        ).scalar()
        
        return result or 0
    
    @staticmethod
    def calculate_session_count(
        db: Session, 
        user_id: int, 
        start_date: datetime, 
        end_date: datetime,
        completed_only: bool = False
    ) -> int:
        """Calcula el número de sesiones en un período"""
        query = db.query(func.count(SesionEstudio.session_id)).filter(
            SesionEstudio.user_id == user_id,
            SesionEstudio.fecha_inicio >= start_date,
            SesionEstudio.fecha_inicio <= end_date
        )
        
        if completed_only:
            query = query.filter(SesionEstudio.fue_completada == True)
        
        return query.scalar() or 0
    
    @staticmethod
    def calculate_completion_rate(db: Session, user_id: int, start_date: datetime, end_date: datetime) -> float:
        """Calcula la tasa de completitud de sesiones"""
        total = DashboardCalculator.calculate_session_count(db, user_id, start_date, end_date)
        completed = DashboardCalculator.calculate_session_count(db, user_id, start_date, end_date, completed_only=True)
        
        if total == 0:
            return 0.0
        
        return round((completed / total) * 100, 2)
    
    @staticmethod
    def get_daily_breakdown(db: Session, user_id: int, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Obtiene el desglose diario de estudio"""
        current_date = start_date.date()
        end = end_date.date()
        daily_data = []
        
        while current_date <= end:
            day_start = datetime.combine(current_date, datetime.min.time())
            day_end = datetime.combine(current_date, datetime.max.time())
            
            total_minutes = DashboardCalculator.calculate_total_minutes(db, user_id, day_start, day_end)
            total_sessions = DashboardCalculator.calculate_session_count(db, user_id, day_start, day_end)
            completed_sessions = DashboardCalculator.calculate_session_count(db, user_id, day_start, day_end, completed_only=True)
            completion_rate = DashboardCalculator.calculate_completion_rate(db, user_id, day_start, day_end)
            
            daily_data.append({
                "date": current_date,
                "total_minutes": total_minutes,
                "total_sessions": total_sessions,
                "completed_sessions": completed_sessions,
                "completion_rate": completion_rate
            })
            
            current_date += timedelta(days=1)
        
        return daily_data
    
    @staticmethod
    def get_method_usage(db: Session, user_id: int, start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """Calcula el uso de cada método de estudio"""
        query = db.query(
            SesionEstudio.metodo_id,
            Metodo.nombre,
            func.count(SesionEstudio.session_id).label('total_sessions'),
            func.sum(SesionEstudio.duracion_minutos).label('total_minutes')
        ).join(
            Metodo, SesionEstudio.metodo_id == Metodo.metodo_id
        ).filter(
            SesionEstudio.user_id == user_id
        )
        
        if start_date and end_date:
            query = query.filter(
                SesionEstudio.fecha_inicio >= start_date,
                SesionEstudio.fecha_inicio <= end_date
            )
        
        results = query.group_by(SesionEstudio.metodo_id, Metodo.nombre).all()
        
        # Calcular porcentajes
        total_minutes_all = sum(r.total_minutes or 0 for r in results)
        
        method_usage = []
        for result in results:
            minutes = result.total_minutes or 0
            percentage = (minutes / total_minutes_all * 100) if total_minutes_all > 0 else 0
            
            method_usage.append({
                "metodo_id": result.metodo_id,
                "metodo_nombre": result.nombre,
                "total_sessions": result.total_sessions,
                "total_minutes": minutes,
                "total_hours": round(minutes / 60, 2),
                "percentage": round(percentage, 2)
            })
        
        # Ordenar por total_minutes descendente
        method_usage.sort(key=lambda x: x['total_minutes'], reverse=True)
        
        return method_usage
    
    @staticmethod
    def calculate_study_streak(db: Session, user_id: int) -> Dict:
        """Calcula la racha de estudio (días consecutivos)"""
        # Obtener todas las fechas únicas de estudio (ordenadas descendente)
        sessions = db.query(
            func.date(SesionEstudio.fecha_inicio).label('study_date')
        ).filter(
            SesionEstudio.user_id == user_id
        ).distinct().order_by(
            func.date(SesionEstudio.fecha_inicio).desc()
        ).all()
        
        if not sessions:
            return {
                "current_streak": 0,
                "longest_streak": 0,
                "last_study_date": None
            }
        
        study_dates = [s.study_date for s in sessions]
        last_study_date = study_dates[0]
        
        # Calcular racha actual
        current_streak = 0
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # La racha es válida si estudió hoy o ayer
        if last_study_date in [today, yesterday]:
            current_streak = 1
            expected_date = last_study_date - timedelta(days=1)
            
            for study_date in study_dates[1:]:
                if study_date == expected_date:
                    current_streak += 1
                    expected_date -= timedelta(days=1)
                else:
                    break
        
        # Calcular racha más larga
        longest_streak = 1
        temp_streak = 1
        
        for i in range(1, len(study_dates)):
            diff = (study_dates[i-1] - study_dates[i]).days
            if diff == 1:
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            else:
                temp_streak = 1
        
        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "last_study_date": last_study_date
        }
    
    @staticmethod
    def get_most_productive_day(db: Session, user_id: int, month: int, year: int) -> Optional[str]:
        """Encuentra el día de la semana más productivo del mes"""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year, 12, 31, 23, 59, 59)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        # Obtener minutos por día de la semana
        sessions = db.query(
            extract('dow', SesionEstudio.fecha_inicio).label('day_of_week'),
            func.sum(SesionEstudio.duracion_minutos).label('total_minutes')
        ).filter(
            SesionEstudio.user_id == user_id,
            SesionEstudio.fecha_inicio >= start_date,
            SesionEstudio.fecha_inicio <= end_date
        ).group_by(
            extract('dow', SesionEstudio.fecha_inicio)
        ).order_by(
            func.sum(SesionEstudio.duracion_minutos).desc()
        ).first()
        
        if not sessions:
            return None
        
        days = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
        return days[int(sessions.day_of_week)]