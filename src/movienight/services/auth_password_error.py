from fastapi import HTTPException, status


def raise_invalid_password():
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=(
            "Password must contain at least one lowercase letter, "
            "an uppercase letter, a digit, and a special character."
        ),
    )
