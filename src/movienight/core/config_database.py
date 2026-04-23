from pydantic import BaseModel


class DatabaseSettingsMixin(BaseModel):
    database_url: str = "sqlite:///./movienight.db"
    sqlite_proxy_url: str = "http://sqlite-proxy:9000"