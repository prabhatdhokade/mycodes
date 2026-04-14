"""Tests for authentication service."""

from __future__ import annotations

import pytest

from optima_ai.core.exceptions import AuthenticationError
from optima_ai.services.auth import AuthService


class TestAuthService:
    @pytest.fixture
    def auth(self):
        return AuthService()

    def test_password_hashing(self, auth):
        hashed = auth.hash_password("secret123")
        assert hashed != "secret123"
        assert auth.verify_password("secret123", hashed)
        assert not auth.verify_password("wrong", hashed)

    def test_create_and_validate_token(self, auth):
        token = auth.create_access_token("user-1", scopes=["read", "write"])
        payload = auth.validate_token(token)
        assert payload.sub == "user-1"
        assert "read" in payload.scopes

    def test_invalid_token_raises(self, auth):
        with pytest.raises(AuthenticationError):
            auth.validate_token("invalid.token.here")

    def test_token_pair(self, auth):
        pair = auth.create_token_pair("user-1", scopes=["admin"])
        assert pair.access_token
        assert pair.refresh_token
        assert pair.token_type == "bearer"
        assert pair.expires_in > 0

        access_payload = auth.validate_token(pair.access_token)
        assert access_payload.sub == "user-1"

    def test_refresh_token_flow(self, auth):
        pair = auth.create_token_pair("user-1")
        new_access = auth.refresh_access_token(pair.refresh_token)
        payload = auth.validate_token(new_access)
        assert payload.sub == "user-1"
