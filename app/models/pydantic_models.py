from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# =========================================================
# --- MÓDULOS DE GIAN (Sesiones, Flashcards, Comunidad) ---
# =========================================================

# --- Schemas para Sesiones (Actualizado con campo 'descripcion') ---
class SessionBase(BaseModel):
    user_id: int
    metodo_id: int

class SessionCreate(SessionBase):
    fecha_inicio: datetime = datetime.now()
    descripcion: Optional[str] = None  # NUEVO: Coincide con la BD

class SessionUpdate(BaseModel):
    duracion_minutos: Optional[int] = None
    fue_completada: Optional[bool] = None
    descripcion: Optional[str] = None  # NUEVO

class SessionOut(SessionBase):
    session_id: int
    fecha_inicio: datetime
    duracion_minutos: int
    fue_completada: bool
    descripcion: Optional[str] = None  # NUEVO

    class Config:
        from_attributes = True


# --- Schemas para Flashcards ---
class FlashcardBase(BaseModel):
    question: str
    answer: str
    is_reversed: bool = False
    flashcard_color: Optional[str] = None

class FlashcardCreate(FlashcardBase):
    card_user: int

class FlashcardOut(FlashcardBase):
    card_id: int
    is_active: bool
    card_user: int
    collection: int

    class Config:
        from_attributes = True


# --- Schemas para Colecciones ---
class CollectionBase(BaseModel):
    collection_name: str
    collection_color: str

class CollectionCreate(CollectionBase):
    is_active: bool = True

class CollectionOut(CollectionBase):
    collection_id: int
    is_active: bool

    class Config:
        from_attributes = True

class CollectionOutWithCards(CollectionOut):
    flashcards: List[FlashcardOut] = []

    class Config:
        from_attributes = True


# --- Schemas para Comunidad (Posts y Likes) ---
class LikeBase(BaseModel):
    user_id: int 

class LikeCreate(LikeBase):
    pass

class LikeOut(LikeBase):
    like_id: int
    post_id: int
    like_date: datetime
    
    class Config:
        from_attributes = True

class PostBase(BaseModel):
    image_url: str
    description: Optional[str] = None

class PostCreate(PostBase):
    user_id: int

class PostUpdate(BaseModel):
    description: Optional[str] = None
    active: Optional[bool] = None

class PostOut(PostBase):
    post_id: int
    user_id: int
    active: bool
    publish_date: datetime
    
    class Config:
        from_attributes = True

class PostOutWithLikes(PostOut):
    likes: List[LikeOut] = []
    
    class Config:
        from_attributes = True


# =========================================================
# --- MÓDULOS DE FLORIAN (Auth, Perfil, Métodos, Diagnóstico) ---
# =========================================================

# --- Schemas para Usuario y Autenticación ---

class UserBase(BaseModel):
    username: str
    email: EmailStr  # Requiere 'pip install pydantic[email]'
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

# 1. Registro (Recibe password plano)
class UserRegister(UserBase):
    password: str

# 2. Login (Recibe identificador y password)
class UserLogin(BaseModel):
    identifier: str  # Puede ser username o email
    password: str

# 3. Perfil de Usuario (Salida de la API)
class UserOut(UserBase):
    user_id: int
    is_premium: Optional[bool] = None
    level: int
    total_studied_time: int
    diagnostic_completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 4. Actualización de Perfil (Entrada PUT)
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    # No incluimos username/email/password aquí por seguridad en este endpoint
    
# 5. Token de Respuesta
class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str


# --- Schemas para Métodos de Estudio ---

class MetodoOut(BaseModel):
    metodo_id: int
    nombre: str
    descripcion: str
    tipo_aprendizaje_compatible: str

    class Config:
        from_attributes = True

class UsuarioMetodoOut(BaseModel):
    user_id: int
    metodo_id: int
    es_recomendado: bool
    es_utilizado: bool
    
    class Config:
        from_attributes = True


# --- Schemas para Diagnóstico (NUEVO) ---

# Opciones de respuesta
class DiagnosticOptionOut(BaseModel):
    option_id: int
    option_text: str
    
    class Config:
        from_attributes = True

# Preguntas del diagnóstico
class DiagnosticQuestionOut(BaseModel):
    question_id: int
    question_text: str
    question_order: int
    options: List[DiagnosticOptionOut] = []  # Lista anidada de opciones
    
    class Config:
        from_attributes = True

# Entrada: Una respuesta individual del usuario
class DiagnosticResponseIn(BaseModel):
    question_id: int
    option_id: int

# Entrada: Formulario completo enviado por el usuario
class DiagnosticFormIn(BaseModel):
    # El user_id se saca del token, no es necesario enviarlo en el JSON si hay auth
    responses: List[DiagnosticResponseIn]

# Salida: Resultado del diagnóstico
class DiagnosticResultOut(BaseModel):
    message: str
    method_recommendation: MetodoOut
    diagnostic_completed: bool