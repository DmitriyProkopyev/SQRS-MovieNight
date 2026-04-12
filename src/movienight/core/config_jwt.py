from pydantic import BaseModel


class JwtSettingsMixin(BaseModel):
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24
