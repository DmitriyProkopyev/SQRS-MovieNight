from fastapi import HTTPException, status


def ensure_password_has_no_personal_info(
    password: str,
    username: str,
) -> None:
    lowered_password = password.lower()
    lowered_username = username.lower()

    if lowered_username and lowered_username in lowered_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Password cannot contain public "
                "personal information, such as username."
            ),
        )
