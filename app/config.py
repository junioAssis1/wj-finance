import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "WJ Finance - Sistema de Gerenciamento de Empréstimos"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "wj-finance-super-secret-key-2026-loan-management")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./wj_finance.db")

    class Config:
        env_file = ".env"

settings = Settings()
