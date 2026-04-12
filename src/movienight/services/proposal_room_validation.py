from fastapi import HTTPException, status

from movienight.core.slots import ROOMS


def normalize_room(room: str) -> str:
    return room.strip()


def ensure_existing_room(room: str) -> str:
    normalized = normalize_room(room)
    if normalized in ROOMS:
        return normalized

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Proposals can only be created in already existing rooms.",
    )
