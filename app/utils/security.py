from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from app.config import get_settings
import bcrypt


settings = get_settings()



def hash_password(password: str) -> str:
    """
    Encripta la contraseña usando bcrypt directamente
    """
    # Convertir la contraseña a bytes
    password_bytes = password.encode('utf-8')
    
    # Truncar si es necesario (bcrypt límite: 72 bytes)
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Generar salt y hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si la contraseña coincide con el hash
    """
    try:
        plain_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        
        # Truncar la contraseña plana si es necesario
        if len(plain_bytes) > 72:
            plain_bytes = plain_bytes[:72]
            
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Crear un token JWT
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()
        })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt

def decode_access_token(token: str) -> dict: 
    """
    Decodificar el token JWT
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def verify_token(token:str)->Optional[dict]:
    """
    Verifca si el toquen es valido y no ha expitrado
    """

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("user_id")
        username: str = payload.get("username")
        
        if user_id is None or username is None:
            return None
            
        return {"user_id": user_id, "username": username}
    except JWTError:
        return None