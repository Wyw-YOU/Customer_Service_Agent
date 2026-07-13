import pytest
from fastapi import HTTPException, status

from app.auth import jwt as jwt_auth


def test_create_and_decode_access_token_round_trip(monkeypatch):
    monkeypatch.setattr(jwt_auth.settings, "jwt_secret", "unit-test-secret")
    monkeypatch.setattr(jwt_auth.settings, "jwt_expire_minutes", 15)

    token = jwt_auth.create_access_token(user_id=42, role="CUSTOMER_SERVICE")
    payload = jwt_auth.decode_access_token(token)

    assert payload["sub"] == "42"
    assert payload["role"] == "CUSTOMER_SERVICE"
    assert "exp" in payload


def test_decode_access_token_rejects_invalid_token(monkeypatch):
    monkeypatch.setattr(jwt_auth.settings, "jwt_secret", "unit-test-secret")

    with pytest.raises(HTTPException) as exc:
        jwt_auth.decode_access_token("not-a-jwt")

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.detail == "Invalid token"


def test_role_levels_are_monotonic_for_permission_checks():
    assert jwt_auth.ROLES == {"USER": 1, "CUSTOMER_SERVICE": 2, "ADMIN": 3}
    assert jwt_auth.ROLES["USER"] < jwt_auth.ROLES["CUSTOMER_SERVICE"] < jwt_auth.ROLES["ADMIN"]


@pytest.mark.asyncio
async def test_require_role_allows_equal_or_higher_role():
    checker = jwt_auth.require_role("CUSTOMER_SERVICE")

    assert await checker({"role": "CUSTOMER_SERVICE"}) == {"role": "CUSTOMER_SERVICE"}
    assert await checker({"role": "ADMIN"}) == {"role": "ADMIN"}


@pytest.mark.asyncio
async def test_require_role_rejects_lower_role():
    checker = jwt_auth.require_role("CUSTOMER_SERVICE")

    with pytest.raises(HTTPException) as exc:
        await checker({"role": "USER"})

    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc.value.detail == "Insufficient permissions"
