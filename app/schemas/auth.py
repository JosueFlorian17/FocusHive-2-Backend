from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
import re 

class RegisterSchema(BaseModel):
    username: str =Field(..., min_length=3, max_length=45)
    email: EmailStr
    password:str = Field(..., min_length=8)
    confirm_password:str = Field(..., min_length=8)

    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('El username solo puede contener letras, números y guiones bajos')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        if not re.search(r'[0-9]', v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Las contraseñas no coinciden')
        return v

class UserResponse(BaseModel):
    user_id:int
    username:str
    email:str
    is_premium:bool
    level:int
    total_studied_time:int

    class Config:
        from_attributes = True
    
class RegisterResponse(BaseModel):
    message:str
    user: UserResponse

class LoginSchema(BaseModel):
    username:str=Field(..., min_length=3)
    password:str=Field(..., min_length=8)

class TokenResponse(BaseModel):
    access_token:str
    token_type:str="bearer"
    user:UserResponse

class TokenData(BaseModel):
    user_id: Optional[int]=None
    username: Optional[int]=None

    

