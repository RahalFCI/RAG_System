from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str
    model_name: str = "gemini-3-flash-preview"
    api_key: str = "AIzaSyCoVyIzi_SwLvtUdp54hVQzrfEPH3t3P5o"
  


    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE: int
    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_URL: Optional[str] = None
    COHERE_API_KEY: Optional[str] = None

    GENERATION_MODEL_ID: Optional[str] = None
    EMBEDDING_MODEL_ID: Optional[str] = None
    EMBEDDING_MODEL_SIZE: Optional[int] = None
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_GENERATION_MODEL_ID: Optional[str] = "gemini-2.0-flash"
    GEMINI_EMBEDDING_MODEL_ID: Optional[str] = "text-embedding-004"
    INPUT_DAFAULT_MAX_CHARACTERS: Optional[int] = None
    GENERATION_DAFAULT_MAX_TOKENS: Optional[int] = None
    GENERATION_DAFAULT_TEMPERATURE: Optional[float] = None

    VECTOR_DB_BACKEND : str
    VECTOR_DB_PATH : str
    VECTOR_DB_PGVEC_INDEX_THRESHOLD: Optional[int] = 100
    VECTOR_DB_DISTANCE_METHOD: Optional[str] = None

    PRIMARY_LANG: str = "ar"
    DEFAULT_LANG: str = "ar"
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    
    # Database Config
    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_MAIN_DATABASE: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

def get_settings():
    return Settings()
