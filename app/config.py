import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

ACCESS_TOKEN_EXPIRES_MINUTES = 30

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    R2_ACCOUNT_ID: str
    R2_ACCESS_KEY_ID: str
    R2_SECRET_ACCESS_KEY: str 
    R2_BUCKET_NAME: str
    ENDPOINT_URL: str
    GROQ_API_KEY: str
    OPENROUTER_API_KEY: str
    MATCH_SCORE_FLOOR: float = 0.55
    MATCH_SCORE_CEILING: float = 0.95

    model_config = SettingsConfigDict(env_file=os.path.join(BASE_DIR, ".env"), env_file_encoding="utf-8")



setting = Settings() # type: ignore


