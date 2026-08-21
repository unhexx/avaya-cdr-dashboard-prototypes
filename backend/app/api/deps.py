"""Общие зависимости: опциональный HTTP Basic."""

import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.config import get_settings

_basic = HTTPBasic(auto_error=False)


async def optional_basic_auth(
    credentials: HTTPBasicCredentials | None = Depends(_basic),  # noqa: B008
) -> None:
    """Если APP_BASIC_AUTH_USER пуст — открытый API (только localhost в compose)."""
    settings = get_settings()
    expected_user = settings.app_basic_auth_user
    if not expected_user:
        return
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Basic"},
        )
    user_ok = secrets.compare_digest(credentials.username, expected_user)
    pass_ok = secrets.compare_digest(credentials.password, settings.app_basic_auth_password)
    if not (user_ok and pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
