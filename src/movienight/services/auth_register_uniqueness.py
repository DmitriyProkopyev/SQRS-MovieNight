from fastapi import HTTPException, status


def ensure_username_available(
    users_repo,
    username: str,
) -> None:
    existing_user = users_repo.get_by_username(username)
    if existing_user is None:
        return

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Username is already taken.",
    )
