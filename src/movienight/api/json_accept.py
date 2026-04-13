from movienight.api.json_accepted_media_type import (
    accepts_json_media_type,
)
from movienight.api.json_media_type import normalize_media_type


def accept_allows_json(value: str | None) -> bool:
    if not value:
        return True

    for part in value.split(","):
        media_type = normalize_media_type(part)
        if accepts_json_media_type(media_type):
            return True

    return False
