from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Movie Night"
    app_env: str = "dev"
    app_debug: bool = True

    database_url: str = "sqlite:///./movie_night.db"

    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 120

    bootstrap_username: str = "admin"
    bootstrap_password: str = "P@ssw0rd123"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
