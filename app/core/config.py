from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, List
from pydantic import PostgresDsn, validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "Coding Challenges API"
    API_V1_STR: str = "/api/v1"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # PostgreSQL settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_PORT: str = "5432"
    POSTGRES_SCHEMA: str = "public"
    POSTGRES_URI: Optional[PostgresDsn] = None
    
    @validator("POSTGRES_URI", pre=True)
    def assemble_postgres_uri(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_HOST"),
            port=int(values.get("POSTGRES_PORT")),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()