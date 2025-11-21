from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.auth import (
    RegisterSchema, 
    RegisterResponse, 
    LoginSchema,
    TokenResponse,
    UserResponse
)
from app.services.auth_service import AuthService
from app.api.dependencies import get_current_user
from app.models.user import Usuario

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registro de nuevo usuario",
    description="Crea una nueva cuenta de usuario con encriptación de contraseña (Req. Funcional #1, Req. No Funcional #4)"
)
async def register(
    data: RegisterSchema,
    db: Session = Depends(get_db)
):
    """
    Registra un nuevo usuario en FocusHive.
    
    - **username**: Nombre de usuario único (3-45 caracteres, solo letras, números y _)
    - **email**: Correo electrónico válido
    - **password**: Contraseña segura (mínimo 8 caracteres, debe contener mayúscula, minúscula y número)
    - **confirm_password**: Confirmación de contraseña
    
    Retorna los datos del usuario creado.
    """
    
    new_user = AuthService.register(db, data)
    
    return RegisterResponse(
        message="Usuario registrado exitosamente",
        user=UserResponse.from_orm(new_user)
    )



@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión",
    description="Autentica al usuario y genera un token de sesión (Req. Funcional #2 y #9)"
)
async def login(
    data: LoginSchema,
    db: Session = Depends(get_db)
):
    """
    Inicia sesión en FocusHive.
    
    - **username**: Nombre de usuario
    - **password**: Contraseña
    
    Retorna un token JWT para autenticación y los datos del usuario.
    El token debe incluirse en el header 'Authorization: Bearer <token>' en requests posteriores.
    """
    
    result = AuthService.login(db, data)
    
    return TokenResponse(
        access_token=result["access_token"],
        token_type=result["token_type"],
        user=UserResponse.from_orm(result["user"])
    )



@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obtener usuario actual",
    description="Obtiene la información del usuario autenticado"
)
async def get_me(
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene los datos del usuario autenticado mediante el token JWT.
    

    """
    return UserResponse.from_orm(current_user)



@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Cerrar sesión",
    description="Invalida la sesión del usuario"
)
async def logout(
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cierra la sesión del usuario.
    
    Nota: Como usamos JWT stateless, el logout se maneja en el frontend
    eliminando el token. Este endpoint sirve para validar que el token
    sea válido antes de eliminarlo.
    """
    return {
        "message": f"Sesión cerrada exitosamente para {current_user.username}",
        "detail": "Elimina el token del cliente"
    }