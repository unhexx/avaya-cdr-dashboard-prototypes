"""Общие фикстуры: кэш настроек сбрасывается между тестами."""

from collections.abc import Iterator

import pytest

from app.config import get_settings
from app.db import reset_engine
from app.services.recordings import reset_recordings_service


@pytest.fixture(autouse=True)
def _reset_singletons() -> Iterator[None]:
    get_settings.cache_clear()
    reset_engine()
    reset_recordings_service()
    yield
    get_settings.cache_clear()
    reset_engine()
    reset_recordings_service()
