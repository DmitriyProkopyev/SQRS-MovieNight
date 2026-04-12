from fastapi import HTTPException, status


def ensure_not_authenticated_for_login(current_user) -> None:
    if current_user is None:
        return

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="User is already authenticated.",
    )
