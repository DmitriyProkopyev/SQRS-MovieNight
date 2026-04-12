from fastapi import HTTPException, status


def raise_malformed_auth_request():
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Malformed authentication request.",
    )
