from pydantic_settings import BaseSettings, SettingsConfigDict

from movienight.core.config_app import AppSettingsMixin
from movienight.core.config_database import DatabaseSettingsMixin
from movienight.core.config_default_user import (
    DefaultUserSettingsMixin,
)
from movienight.core.config_jwt import JwtSettingsMixin


class Settings(
    AppSettingsMixin,
    DatabaseSettingsMixin,
    JwtSettingsMixin,
    DefaultUserSettingsMixin,
    BaseSettings,
):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
