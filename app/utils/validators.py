from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import Usuario
import re

class UserValidator:
    """Validaciones personalizadas para usuarios"""
    
    @staticmethod
    def validate_username_available(db: Session, username: str, exclude_user_id: int = None) -> bool:
        """
        Verifica si un username está disponible.
        
        Args:
            db: Sesión de base de datos
            username: Username a verificar
            exclude_user_id: ID de usuario a excluir de la búsqueda (para updates)
        
        Returns:
            True si está disponible, lanza excepción si no
        """
        query = db.query(Usuario).filter(Usuario.username == username)
        
        if exclude_user_id:
            query = query.filter(Usuario.user_id != exclude_user_id)
        
        existing_user = query.first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El username '{username}' ya está en uso"
            )
        
        return True
    
    @staticmethod
    def validate_email_available(db: Session, email: str, exclude_user_id: int = None) -> bool:
        """
        Verifica si un email está disponible.
        
        Args:
            db: Sesión de base de datos
            email: Email a verificar
            exclude_user_id: ID de usuario a excluir de la búsqueda (para updates)
        
        Returns:
            True si está disponible, lanza excepción si no
        """
        query = db.query(Usuario).filter(Usuario.email == email)
        
        if exclude_user_id:
            query = query.filter(Usuario.user_id != exclude_user_id)
        
        existing_email = query.first()
        
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El email '{email}' ya está registrado"
            )
        
        return True
    
    @staticmethod
    def validate_avatar_url(url: str) -> bool:
        """
        Valida que la URL del avatar sea válida.
        
        Args:
            url: URL a validar
        
        Returns:
            True si es válida, lanza excepción si no
        """
        if not url:
            return True
        
        # Patrón básico para URLs de imágenes
        url_pattern = re.compile(
            r'^https?://'  # http:// o https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # dominio
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # o IP
            r'(?::\d+)?'  # puerto opcional
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La URL del avatar no es válida"
            )
        
        # Validar extensiones de imagen comunes
        valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg')
        if not any(url.lower().endswith(ext) for ext in valid_extensions):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La URL debe apuntar a una imagen válida (.jpg, .jpeg, .png, .gif, .webp, .svg)"
            )
        
        return True