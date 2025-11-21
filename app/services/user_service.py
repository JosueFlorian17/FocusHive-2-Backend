from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import Optional, List
from app.models.user import Usuario
from app.schemas.user import UserUpdateSchema, ChangePasswordSchema
from app.utils.security import hash_password, verify_password
from app.utils.validators import UserValidator

class UserService:
    """Servicio para operaciones CRUD del perfil de usuario"""
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Usuario:
        """
        Obtiene un usuario por su ID.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
        
        Returns:
            Usuario encontrado
        
        Raises:
            HTTPException: Si el usuario no existe
        """
        user = db.query(Usuario).filter(Usuario.user_id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {user_id} no encontrado"
            )
        
        return user
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Usuario:
        """
        Obtiene un usuario por su username.
        
        Args:
            db: Sesión de base de datos
            username: Username del usuario
        
        Returns:
            Usuario encontrado
        
        Raises:
            HTTPException: Si el usuario no existe
        """
        user = db.query(Usuario).filter(Usuario.username == username).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario '{username}' no encontrado"
            )
        
        return user
    
    @staticmethod
    def get_all_users(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[Usuario]:
        """
        Obtiene una lista paginada de usuarios.
        
        Args:
            db: Sesión de base de datos
            skip: Número de registros a saltar (para paginación)
            limit: Número máximo de registros a retornar
            search: Término de búsqueda opcional (busca en username y full_name)
        
        Returns:
            Lista de usuarios
        """
        query = db.query(Usuario)
        
        # Aplicar filtro de búsqueda si existe
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (Usuario.username.like(search_pattern)) |
                (Usuario.full_name.like(search_pattern))
            )
        
        users = query.offset(skip).limit(limit).all()
        return users
    
    @staticmethod
    def update_user_profile(
        db: Session, 
        user_id: int, 
        update_data: UserUpdateSchema
    ) -> Usuario:
        """
        Actualiza el perfil de un usuario.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario a actualizar
            update_data: Datos a actualizar
        
        Returns:
            Usuario actualizado
        
        Raises:
            HTTPException: Si hay errores de validación o el usuario no existe
        """
        # Obtener usuario actual
        user = UserService.get_user_by_id(db, user_id)
        
        # Crear diccionario solo con los campos que no son None
        update_dict = update_data.model_dump(exclude_unset=True, exclude_none=True)
        
        # Si no hay campos para actualizar
        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se proporcionaron campos para actualizar"
            )
        
        try:
            # Validar username si se está actualizando
            if 'username' in update_dict:
                UserValidator.validate_username_available(
                    db, 
                    update_dict['username'], 
                    exclude_user_id=user_id
                )
            
            # Validar email si se está actualizando
            if 'email' in update_dict:
                UserValidator.validate_email_available(
                    db, 
                    update_dict['email'], 
                    exclude_user_id=user_id
                )
            
            # Validar avatar_url si se está actualizando
            if 'avatar_url' in update_dict:
                UserValidator.validate_avatar_url(update_dict['avatar_url'])
            
            # Actualizar campos
            for field, value in update_dict.items():
                setattr(user, field, value)
            
            db.commit()
            db.refresh(user)
            
            return user
            
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error de integridad: verifica que los datos sean únicos"
            )
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar el perfil: {str(e)}"
            )
    
    @staticmethod
    def change_password(
        db: Session, 
        user_id: int, 
        password_data: ChangePasswordSchema
    ) -> Usuario:
        """
        Cambia la contraseña de un usuario.
        Implementa el requisito no funcional
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            password_data: Datos de la contraseña (actual, nueva, confirmación)
        
        Returns:
            Usuario actualizado
        
        Raises:
            HTTPException: Si la contraseña actual es incorrecta
        """
        # Obtener usuario
        user = UserService.get_user_by_id(db, user_id)
        
        # Verificar contraseña actual
        if not verify_password(password_data.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña actual es incorrecta"
            )
        
        # Verificar que la nueva contraseña sea diferente
        if verify_password(password_data.new_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La nueva contraseña debe ser diferente a la actual"
            )
        
        try:
            # Actualizar contraseña con encriptación
            user.password_hash = hash_password(password_data.new_password)
            
            db.commit()
            db.refresh(user)
            
            return user
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al cambiar la contraseña: {str(e)}"
            )
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """
        Elimina un usuario 
        Implementa el requisito funcional 
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario a eliminar
        
        Returns:
            True si se eliminó correctamente
        
        Raises:
            HTTPException: Si el usuario no existe o hay error en la eliminación
        """
        # Obtener usuario
        user = UserService.get_user_by_id(db, user_id)
        
        try:
            db.delete(user)
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al eliminar el usuario: {str(e)}"
            )
    
    @staticmethod
    def get_user_statistics(db: Session, user_id: int) -> dict:
        """
        Obtiene estadísticas básicas del usuario.
        Útil para el dashboard
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
        
        Returns:
            Diccionario con estadísticas del usuario
        """
        user = UserService.get_user_by_id(db, user_id)
        
        # Aquí puedes agregar consultas adicionales para obtener más estadísticas
        # Por ejemplo, contar sesiones de estudio, posts, etc.
        
        return {
            "user_id": user.user_id,
            "username": user.username,
            "level": user.level,
            "total_studied_time": user.total_studied_time,
            "is_premium": user.is_premium,
            "member_since": user.created_at.strftime("%Y-%m-%d") if user.created_at else None
        }