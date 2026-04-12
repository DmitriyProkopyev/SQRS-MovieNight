from movienight.core.config import settings


def get_raw_default_user_credentials() -> tuple[str | None, str | None]:
    return settings.default_username, settings.default_password
