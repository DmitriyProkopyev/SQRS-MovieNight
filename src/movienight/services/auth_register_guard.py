from fastapi import HTTPException, status


def ensure_registration_allowed(current_user) -> None:
    if current_user is None:
        return

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Log out before creating a new account.",
    )
