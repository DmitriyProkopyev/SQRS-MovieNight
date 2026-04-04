from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=255)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "admin",
                "password": "P@ssw0rd123",
            }
        }
    )


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=255)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "new_user",
                "password": "StrongPass123",
            }
        }
    )


class UserResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "username": "admin",
            }
        },
    )

    id: int
    username: str


class LoginResponse(BaseModel):
    access_token: str = Field(
        description="JWT access token for authenticated requests."
    )
    token_type: str = Field(
        default="bearer",
        description="Authentication scheme type."
    )
    user: UserResponse

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "<JWT_TOKEN>",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "username": "admin",
                },
            }
        }
    )


class MessageResponse(BaseModel):
    message: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "User 'admin' was logged out."
            }
        }
    )