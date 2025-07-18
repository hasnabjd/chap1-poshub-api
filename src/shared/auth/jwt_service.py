from datetime import datetime, timedelta
from typing import List, Optional

import jwt
from fastapi import HTTPException, status

from src.shared.config.jwt_config import jwt_settings


class JWTService:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = jwt_settings.access_token_expire_minutes

    def create_access_token(
        self, 
        user_id: str, 
        scopes: List[str], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Crée un token JWT avec les scopes de l'utilisateur
        
        Args:
            user_id: Identifiant unique de l'utilisateur
            scopes: Liste des permissions/scopes (ex: ["orders:write", "orders:read"])
            expires_delta: Durée de validité du token
            
        Returns:
            Token JWT encodé
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.access_token_expire_minutes
            )

        payload = {
            "user_id": user_id,
            "scopes": scopes,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> dict:
        """
        Vérifie et décode un token JWT
        
        Args:
            token: Token JWT à vérifier
            
        Returns:
            Payload du token décodé
            
        Raises:
            HTTPException: Si le token est invalide ou expiré
        """
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            
            # Vérifier que c'est bien un token d'accès
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token invalide",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expiré",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def verify_scopes(self, token_scopes: List[str], required_scopes: List[str]) -> bool:
        """
        Vérifie que l'utilisateur a les scopes requis
        
        Args:
            token_scopes: Scopes présents dans le token
            required_scopes: Scopes requis pour l'action
            
        Returns:
            True si l'utilisateur a tous les scopes requis
        """
        return all(scope in token_scopes for scope in required_scopes) 