from fastapi import HTTPException, status

from movienight.repositories.users import UserRepository


def load_user_by_id(db, user_id: int):
    user = UserRepository(db).get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found for token.",
        )
    return user
