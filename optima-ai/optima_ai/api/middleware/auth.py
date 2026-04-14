"""Authentication middleware — validates JWT tokens on protected routes."""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from optima_ai.core.exceptions import AuthenticationError
from optima_ai.services.auth import AuthService, TokenPayload

_bearer_scheme = HTTPBearer(auto_error=False)
_auth_service = AuthService()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> TokenPayload:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )
    try:
        return _auth_service.validate_token(credentials.credentials)
    except AuthenticationError as exc:
        raise HTTPException(status_code=exc.status, detail=exc.message)


async def optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> TokenPayload | None:
    if not credentials:
        return None
    try:
        return _auth_service.validate_token(credentials.credentials)
    except AuthenticationError:
        return None
