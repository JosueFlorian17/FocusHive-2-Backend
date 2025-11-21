from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.connection import get_db
from app.api.dependencies import get_current_user
from app.models.user import Usuario
from app.schemas.user import (
    UserDetailResponse,
    UserSummaryResponse,
    UserUpdateSchema,
    ChangePasswordSchema,
    UserActionResponse
)
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

# READ 

@router.get(
    "/me",
    response_model=UserDetailResponse,
    summary="Obtener perfil propio",
    description="Obtiene la información completa del usuario autenticado"
)
async def get_my_profile(
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene el perfil completo del usuario autenticado.
    
    Requiere: Token de autenticación
    
    Retorna todos los detalles del perfil incluyendo:
    - Información básica (username, email, nombre completo)
    - Estadísticas (level, tiempo de estudio)
    - Personalización (avatar, bio)
    - Fechas de creación y actualización
    """
    return UserDetailResponse.from_orm(current_user)



@router.get(
    "/me/stats",
    summary="Obtener estadísticas propias",
    description="Obtiene estadísticas del usuario autenticado"
)
async def get_my_statistics(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas del usuario autenticado.
    Útil para mostrar en el dashboard.
    
    Requiere: Token de autenticación
    """
    stats = UserService.get_user_statistics(db, current_user.user_id)
    return stats



@router.get(
    "/{user_id}",
    response_model=UserDetailResponse,
    summary="Obtener perfil por ID",
    description="Obtiene la información de un usuario específico por su ID"
)
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene el perfil de un usuario específico por su ID.
    
    Requiere: Token de autenticación
    
    Args:
        user_id: ID del usuario a buscar
    
    Retorna la información pública del usuario.
    """
    user = UserService.get_user_by_id(db, user_id)
    return UserDetailResponse.from_orm(user)



@router.get(
    "/username/{username}",
    response_model=UserDetailResponse,
    summary="Obtener perfil por username",
    description="Obtiene la información de un usuario específico por su username"
)
async def get_user_by_username(
    username: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene el perfil de un usuario específico por su username.
    
    Requiere: Token de autenticación
    
    Args:
        username: Username del usuario a buscar
    
    Retorna la información pública del usuario.
    """
    user = UserService.get_user_by_username(db, username)
    return UserDetailResponse.from_orm(user)



@router.get(
    "/",
    response_model=List[UserSummaryResponse],
    summary="Listar usuarios",
    description="Obtiene una lista paginada de usuarios con búsqueda opcional"
)
async def get_all_users(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de registros a retornar"),
    search: Optional[str] = Query(None, description="Buscar por username o nombre completo"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene una lista paginada de usuarios.
    
    Requiere: Token de autenticación
    
    Query Parameters:
        - skip: Número de registros a saltar (para paginación, default: 0)
        - limit: Número máximo de registros (default: 20, max: 100)
        - search: Término de búsqueda para filtrar por username o nombre
    
    Ejemplo de uso:
        - /api/v1/users?skip=0&limit=20
        - /api/v1/users?search=josue
        - /api/v1/users?skip=20&limit=20&search=test
    """
    users = UserService.get_all_users(db, skip=skip, limit=limit, search=search)
    return [UserSummaryResponse.from_orm(user) for user in users]


# UPDATE 
@router.put(
    "/me",
    response_model=UserActionResponse,
    summary="Actualizar perfil propio",
    description="Actualiza la información del perfil del usuario autenticado"
)
async def update_my_profile(
    update_data: UserUpdateSchema,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza el perfil del usuario autenticado.
    
    
    Requiere: Token de autenticación
    
    Campos actualizables:
        - username (único, 3-45 caracteres)
        - email (único, formato válido)
        - full_name (máximo 100 caracteres)
        - bio (máximo 500 caracteres)
        - avatar_url (URL válida de imagen)
    
    Todos los campos son opcionales. Solo se actualizan los campos enviados.
    
    Ejemplo de request body:
```json
    {
        "full_name": "Josué Florián",
        "bio": "Desarrollador backend apasionado por crear APIs eficientes",
        "avatar_url": "https://example.com/avatar.jpg"
    }
```
    """
    user_id_to_update=current_user.user_id
    
    updated_user = UserService.update_user_profile(
        db, 
        user_id_to_update, 
        update_data
    )
    
    return UserActionResponse(
        message="Perfil actualizado exitosamente",
        user=UserDetailResponse.from_orm(updated_user)
    )

@router.patch(
    "/me/password",
    response_model=UserActionResponse,
    summary="Cambiar contraseña",
    description="Cambia la contraseña del usuario autenticado"
)
async def change_my_password(
    password_data: ChangePasswordSchema,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cambia la contraseña del usuario autenticado.
    
    Implementa el requisito no funcional
    
    Requiere: Token de autenticación
    
    Campos requeridos:
        - current_password: Contraseña actual
        - new_password: Nueva contraseña (mínimo 8 caracteres, debe contener mayúscula, minúscula y número)
        - confirm_new_password: Confirmación de la nueva contraseña
    
    Validaciones:
        - La contraseña actual debe ser correcta
        - La nueva contraseña debe cumplir con los requisitos de seguridad
        - Las contraseñas nuevas deben coincidir
        - La nueva contraseña debe ser diferente a la actual
    
    Ejemplo de request body:
```json
    {
        "current_password": "OldPassword123",
        "new_password": "NewPassword456",
        "confirm_new_password": "NewPassword456"
    }
```
    """
    updated_user = UserService.change_password(
        db,
        current_user.user_id,
        password_data
    )
    
    return UserActionResponse(
        message="Contraseña cambiada exitosamente",
        user=UserDetailResponse.from_orm(updated_user)
    )

# DELETE

@router.delete(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Eliminar cuenta propia",
    description="Elimina la cuenta del usuario autenticado (Req. Funcional #3)"
)
async def delete_my_account(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Elimina la cuenta del usuario autenticado.
    
    
    Requiere: Token de autenticación
    
    ADVERTENCIA: Esta acción es irreversible.
    
    Se eliminarán todos los datos asociados al usuario:
        - Sesiones de estudio
        - Posts y likes
        - Flashcards
        - Configuraciones personalizadas
    
    Retorna un mensaje de confirmación.
    """
    UserService.delete_user(db, current_user.user_id)
    
    return {
        "message": f"Cuenta de {current_user.username} eliminada exitosamente",
        "detail": "Todos los datos asociados han sido eliminados"
    }

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar usuario por ID (Admin)",
    description="Elimina un usuario específico por su ID (requiere permisos de admin)"
)
async def delete_user_by_id(
    user_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Elimina un usuario específico por su ID.
    
    Este endpoint debería estar protegido por permisos de administrador.
    Por ahora, cualquier usuario autenticado puede usarlo (ajustar en producción).
    
    Requiere: Token de autenticación
    
    Args:
        user_id: ID del usuario a eliminar
    
    ADVERTENCIA: Esta acción es irreversible.
    """

    
    UserService.delete_user(db, user_id)
    
    return {
        "message": f"Usuario con ID {user_id} eliminado exitosamente",
        "deleted_by": current_user.username
    }