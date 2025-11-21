from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL:str ="mysql+pymysql://root:KRoltSjEZRLlSRSKOlbxjvrkKjPaaWPf@trolley.proxy.rlwy.net:56041/railway"
    DEBUG: bool = True   # ← AGREGAR ESTO

    #Seguridad
    ACCESS_TOKEN_EXPIRE_MINUTES:int =30

    #App
    APP_NAME: str ="FocusHive API"

    SECRET_KEY:  str="clave-secreta-cambia-en-produccion"

    ALGORITHM :str ="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int =30
    DEBUG=True

    class config:
        env_file=".env"

@lru_cache()
def get_settings():
    return Settings()
