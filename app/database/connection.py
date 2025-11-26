from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings
# Importaciones necesarias para tipos personalizados
from sqlalchemy.types import TypeDecorator, String 
import typing as t

# Esto asegura que los datos binarios (como el color) se lean como una cadena de texto
class ColorString(TypeDecorator):
    impl = String(6) # Tipo de implementación en el ORM (String de longitud 6)
    
    # Método que se ejecuta al LEER de la BD
    def process_result_value(self, value: t.Any, dialect: t.Any) -> t.Optional[str]:
        if value is not None and isinstance(value, bytes):
            # Decodificar el binario a UTF-8 (asumiendo que guardaste un HEX)
            return value.decode('utf-8')
        return value

settings=get_settings()

engine=create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency para obtener la sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()