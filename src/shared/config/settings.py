import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration via environment variables."""
    
    # Required environment variables
    STAGE: str = "dev"
    LOG_LEVEL: str = "INFO"
    API_KEY_PARAM: str = "/pos-h/api-key"
    
    # Optional variables
    AWS_REGION: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Returns the configuration settings instance."""
    return settings 