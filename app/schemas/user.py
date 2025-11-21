from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re

# Schema base con campos comunes
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=45)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=255)

# Schema para actualizar perfil (todos los campos son opcionales)
class UserUpdateSchema(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=45)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=255)
    
    @validator('username')
    def validate_username(cls, v):
        if v is not None:
            if not re.match(r'^[a-zA-Z0-9_]+$', v):
                raise ValueError('El username solo puede contener letras, números y guiones bajos')
        return v
    
    class Config:
        # Permitir que al menos un campo esté presente
        anystr_strip_whitespace = True

# Schema para cambiar contraseña
class ChangePasswordSchema(BaseModel):
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)
    confirm_new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        if not re.search(r'[0-9]', v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v
    
    @validator('confirm_new_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Las contraseñas no coinciden')
        return v

# Schema completo de respuesta del usuario
class UserDetailResponse(BaseModel):
    user_id: int
    username: str
    email: str
    full_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    is_premium: bool
    level: int
    total_studied_time: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Schema simplificado (para listas, búsquedas, etc.)
class UserSummaryResponse(BaseModel):
    user_id: int
    username: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    level: int
    is_premium: bool
    
    class Config:
        from_attributes = True

# Schema para confirmar acciones
class UserActionResponse(BaseModel):
    message: str
    user: UserDetailResponse