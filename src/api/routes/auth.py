from datetime import timedelta
from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from src.api.dependencies.auth import jwt_service

router = APIRouter(prefix="/auth", tags=["authentication"])


class TokenRequest(BaseModel):
    """Requête pour générer un token"""

    user_id: str
    scopes: List[str] = []
    expires_in_minutes: int = 30


class TokenResponse(BaseModel):
    """Réponse contenant le token JWT"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    scopes: List[str]


@router.post("/token", response_model=TokenResponse)
async def generate_token(request: TokenRequest) -> TokenResponse:
    """
    Génère un token JWT pour un utilisateur avec les scopes spécifiés

    🚨 ATTENTION: Cette route est à des fins de test/développement uniquement !
    En production, l'authentification doit passer par un système sécurisé.

    Args:
        request: Informations pour générer le token

    Returns:
        Token JWT et métadonnées
    """
    # Créer le token avec les scopes demandés
    token = jwt_service.create_access_token(
        user_id=request.user_id,
        scopes=request.scopes,
        expires_delta=timedelta(minutes=request.expires_in_minutes),
    )

    return TokenResponse(
        access_token=token,
        expires_in=request.expires_in_minutes * 60,  # en secondes
        scopes=request.scopes,
    )


@router.post("/token/orders-write", response_model=TokenResponse)
async def generate_orders_write_token(user_id: str = "test-user") -> TokenResponse:
    """
    Génère un token avec le scope 'orders:write' pour tester la création de commandes

    🚨 ATTENTION: Route de test uniquement !

    Args:
        user_id: ID de l'utilisateur (par défaut: "test-user")

    Returns:
        Token JWT avec scope orders:write
    """
    scopes = ["orders:write", "orders:read"]

    token = jwt_service.create_access_token(
        user_id=user_id, scopes=scopes, expires_delta=timedelta(minutes=60)
    )

    return TokenResponse(
        access_token=token, expires_in=3600, scopes=scopes  # 1 heure en secondes
    )
