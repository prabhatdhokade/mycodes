"""JWT-based authentication and token management.

Handles:
  - Token creation and validation with configurable expiry
  - Secure password hashing with bcrypt
  - Per-user provider token storage (encrypted at rest in production)
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt
from pydantic import BaseModel

from optima_ai.core.config import get_settings
from optima_ai.core.exceptions import AuthenticationError
from optima_ai.core.logging import get_logger

logger = get_logger(__name__)


class TokenPayload(BaseModel):
    sub: str
    exp: datetime
    scopes: list[str] = []
    metadata: dict[str, Any] = {}


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthService:
    """Stateless JWT auth service — pairs with external user store."""

    def __init__(self):
        self.settings = get_settings()

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode(), hashed.encode())

    def create_access_token(
        self,
        subject: str,
        scopes: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        expires_delta: timedelta | None = None,
    ) -> str:
        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=self.settings.jwt_expiry_minutes)
        )
        payload = {
            "sub": subject,
            "exp": expire,
            "scopes": scopes or [],
            "metadata": metadata or {},
        }
        return jwt.encode(payload, self.settings.jwt_secret, algorithm=self.settings.jwt_algorithm)

    def create_refresh_token(self, subject: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(days=30)
        payload = {"sub": subject, "exp": expire, "type": "refresh"}
        return jwt.encode(payload, self.settings.jwt_secret, algorithm=self.settings.jwt_algorithm)

    def create_token_pair(
        self,
        subject: str,
        scopes: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> TokenPair:
        access = self.create_access_token(subject, scopes, metadata)
        refresh = self.create_refresh_token(subject)
        return TokenPair(
            access_token=access,
            refresh_token=refresh,
            expires_in=self.settings.jwt_expiry_minutes * 60,
        )

    def validate_token(self, token: str) -> TokenPayload:
        try:
            payload = jwt.decode(
                token,
                self.settings.jwt_secret,
                algorithms=[self.settings.jwt_algorithm],
            )
            return TokenPayload(**payload)
        except JWTError as exc:
            raise AuthenticationError(f"Token validation failed: {exc}") from exc

    def refresh_access_token(self, refresh_token: str) -> str:
        payload = self.validate_token(refresh_token)
        return self.create_access_token(payload.sub)
