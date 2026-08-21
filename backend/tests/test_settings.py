"""Дефолты настроек: фикстуры включены, живые коннекторы выключены."""

from app.config import Settings


def test_fixture_mode_is_default() -> None:
    settings = Settings(
        _env_file=None,  # type: ignore[call-arg]
    )
    assert settings.use_fixtures is True
    assert settings.enable_live_connectors is False
    assert settings.recordings_allow_encrypted_audio is False


def test_sat_defaults_are_idle() -> None:
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    assert settings.cm_sat_host == ""
    assert settings.ipo_smdr_host == ""
    assert settings.ipo_ssa_url == ""
