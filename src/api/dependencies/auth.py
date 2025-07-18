from typing import Annotated, List

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from src.shared.auth.jwt_service import JWTService
from src.shared.config.jwt_config import jwt_settings


class AuthenticatedUser(BaseModel):
    """Modèle représentant un utilisateur authentifié"""

    user_id: str
    scopes: List[str]


class AuthDependencies:
    def __init__(self, jwt_service: JWTService):
        self.jwt_service = jwt_service
        self.bearer_scheme = HTTPBearer()

    def get_current_user(
        self,
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
    ) -> AuthenticatedUser:
        """
        Dépendance pour obtenir l'utilisateur actuellement authentifié

        Args:
            credentials: Credentials extraites de l'en-tête Authorization

        Returns:
            Utilisateur authentifié avec ses scopes

        Raises:
            HTTPException: Si le token est invalide
        """
        # Vérifier et décoder le token
        payload = self.jwt_service.verify_token(credentials.credentials)

        # Créer l'utilisateur authentifié
        return AuthenticatedUser(
            user_id=payload["user_id"], scopes=payload.get("scopes", [])
        )

    def require_scopes(self, required_scopes: List[str]):
        """
        Crée une dépendance qui vérifie que l'utilisateur a les scopes requis

        Args:
            required_scopes: Liste des scopes requis

        Returns:
            Fonction de dépendance FastAPI
        """

        def _verify_scopes(
            current_user: Annotated[AuthenticatedUser, Depends(self.get_current_user)],
        ) -> AuthenticatedUser:
            """
            Vérifie que l'utilisateur a les scopes requis

            Args:
                current_user: Utilisateur authentifié

            Returns:
                Utilisateur authentifié si les scopes sont valides

            Raises:
                HTTPException: Si l'utilisateur n'a pas les scopes requis
            """
            if not self.jwt_service.verify_scopes(current_user.scopes, required_scopes):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Scopes insuffisants. Requis: {required_scopes}",
                )
            return current_user

        return _verify_scopes


# Configuration globale utilisant les paramètres JWT
jwt_service = JWTService(
    secret_key=jwt_settings.secret_key, algorithm=jwt_settings.algorithm
)
auth_deps = AuthDependencies(jwt_service)

# Dépendances prêtes à l'emploi
GetCurrentUser = Depends(auth_deps.get_current_user)
RequireOrdersWrite = Depends(auth_deps.require_scopes(["orders:write"]))
RequireOrdersRead = Depends(auth_deps.require_scopes(["orders:read"]))
