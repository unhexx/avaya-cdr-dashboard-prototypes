"""Настройки приложения из окружения (без секретов в коде)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Конфигурация процесса API. Имена полей совпадают с .env.example."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_log_level: str = "INFO"
    app_secret_key: str = "change-me-in-local-env"
    app_basic_auth_user: str = ""
    app_basic_auth_password: str = ""

    database_url: str = "postgresql+asyncpg://avaya:avaya@localhost:5432/avaya_cdr"

    recordings_sql_url: str = ""
    recordings_sql_dialect: str = "auto"
    recordings_media_root: str = ""
    recordings_allow_encrypted_audio: bool = False

    redis_url: str = ""

    cm_sat_host: str = ""
    cm_sat_port: int = 5022
    cm_sat_user: str = ""
    cm_sat_password: str = ""
    cm_sat_timeout_seconds: int = 15
    cm_cdr_listen_host: str = "0.0.0.0"
    cm_cdr_listen_port: int = 9000
    cm_cdr_format: str = "expanded"
    cm_snmp_host: str = ""
    cm_snmp_community: str = ""
    cm_snmp_version: str = "2c"

    ipo_smdr_host: str = ""
    ipo_smdr_port: int = 8888
    ipo_snmp_host: str = ""
    ipo_snmp_community: str = ""
    ipo_ssa_url: str = ""
    ipo_ssa_user: str = ""
    ipo_ssa_password: str = ""

    syslog_listen_host: str = "0.0.0.0"
    syslog_listen_port: int = 5514
    syslog_protocol: str = "udp"

    use_fixtures: bool = True
    enable_live_connectors: bool = False
    enable_recording_audio: bool = True


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Кэш настроек на процесс; в тестах сбрасывать через cache_clear()."""
    return Settings()
