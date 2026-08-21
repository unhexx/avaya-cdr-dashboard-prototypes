"""Общие фикстуры: кэш настроек сбрасывается между тестами."""

import pytest

from app.config import get_settings
from app.db import reset_engine


@pytest.fixture(autouse=True)
def _reset_singletons() -> None:
    get_settings.cache_clear()
    reset_engine()
    yield
    get_settings.cache_clear()
    reset_engine()
