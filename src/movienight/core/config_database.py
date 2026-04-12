from pydantic import BaseModel


class DatabaseSettingsMixin(BaseModel):
    database_url: str = "sqlite:///./movienight.db"
