from pydantic import BaseModel


class AppSettingsMixin(BaseModel):
    app_name: str = "Movie Night API"
