from movienight.core.security import create_access_token
from movienight.schemas.auth import LoginResponse, UserResponse


def build_login_response(user) -> LoginResponse:
    token = create_access_token(subject=str(user.id))
    return LoginResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )
