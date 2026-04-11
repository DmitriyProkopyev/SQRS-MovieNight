from pydantic import BaseModel


class DefaultUserSettingsMixin(BaseModel):
    default_username: str | None = None
    default_password: str | None = None
