from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from datetime import timedelta
from app.models.user import Usuario
from app.schemas.auth import RegisterSchema, LoginSchema, UserResponse
from app.utils.security import hash_password, verify_password, create_access_token
from app.config import get_settings

#Obtener la configutacion
settings=get_settings()

class AuthService:
    
    @staticmethod
    def register(db:Session, data:RegisterSchema)->Usuario:
        """
        Registrar un nuevo usuario en el sistema
        """
        #verificar si el username ya existe
        existing_user=db.query(Usuario).filter(Usuario.username==data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El username ya esta en uso"
            )
        
        #Verificar si el email ya existe
        existing_email=db.query(Usuario).filter(Usuario.email==data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo ya ha sido registrado"
            )
        #Crear nuevos usuarios con contrase;a encriptada

        try:
            new_user=Usuario(
                username=data.username,
                email=data.email,
                password_hash=hash_password(data.password),
                is_premium=False,
                level=1,
                total_studied_time=0
            )

            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            return new_user
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error al crear el usuario. Veriica que los datos sean unicos"
            )
        
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno del servidor: {str(e)}"
            )
    @staticmethod
    def login(db:Session, data:LoginSchema)->dict:
        """
        Autentica al usuario y genera un token de sesion
        """

        #buscar usuario por username
        user=db.query(Usuario).filter(Usuario.username==data.username).first()

        #Verificar si el usuario no existe
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        #Verificar contrase;a
        if not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        #Generar token JWT con informacion del usuario
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email
            },
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
    
    @staticmethod
    def get_current_user(db:Session, user_id:int)->Usuario:
        """
        Ovtiene los datos del usuario desde la BD
        """
        user=db.query(Usuario).filter(Usuario.user_id==user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        return user