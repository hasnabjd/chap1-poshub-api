import os

from pydantic_settings import BaseSettings


class JWTSettings(BaseSettings):
    """Configuration pour JWT"""

    # Clé secrète pour signer les tokens JWT
    # En production, utiliser une vraie clé secrète forte
    secret_key: str = os.getenv(
        "JWT_SECRET_KEY", "your-very-secure-secret-key-change-in-production"
    )

    # Algorithme de signature
    algorithm: str = "HS256"

    # Durée de validité du token d'accès (en minutes)
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instance globale des paramètres JWT
jwt_settings = JWTSettings()
