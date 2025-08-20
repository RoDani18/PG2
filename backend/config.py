from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()  # Carga variables desde .env

class Settings(BaseSettings):
    PROJECT_NAME: str = "Asistente IA"
    API_VERSION: str = "v1"

    # Seguridad
    SECRET_KEY: str = os.getenv("SECRET_KEY", "clave_segura")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    # Base de datos
    POSTGRES_URL: str = os.getenv("POSTGRES_URL", "postgresql://usuario:clave@localhost:5432/asistente")
    SQLITE_URL: str = os.getenv("SQLITE_URL", "sqlite:///backend/offline/offline_sqlite.db")

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:8000"
    ]

    # Voz e IA
    VOSK_MODEL_PATH: str = os.getenv("VOSK_MODEL_PATH", "vosk-model-es-0.42")
    LOG_PATH: str = os.getenv("LOG_PATH", "backend/Voz_Asistente/log_asistente.txt")
    INTENCIONES_PATH: str = os.getenv("INTENCIONES_PATH", "backend/Voz_Asistente/intenciones.json")
    TAU_LOW: float = 0.60
    TAU_HIGH: float = 0.90

settings = Settings()
