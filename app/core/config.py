from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, List
from pydantic import PostgresDsn, field_validator, ConfigDict


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
    
    @field_validator("POSTGRES_URI", mode="before")
    @classmethod
    def assemble_postgres_uri(cls, v: Optional[str], info) -> Any:
        if isinstance(v, str):
            return v
        # Get values from the ValidationInfo object
        data = info.data
        return PostgresDsn.build(
            scheme="postgresql",
            username=data.get("POSTGRES_USER"),
            password=data.get("POSTGRES_PASSWORD"),
            host=data.get("POSTGRES_HOST"),
            port=int(data.get("POSTGRES_PORT")),
            path=f"{data.get('POSTGRES_DB') or ''}",
        )
    
    model_config = ConfigDict(
        case_sensitive=True,
        env_file=".env"
    )


settings = Settings()