from movienight.api.json_media_type import normalize_media_type


def content_type_is_json(value: str | None) -> bool:
    if not value:
        return True

    media_type = normalize_media_type(value)
    return media_type == "application/json" or media_type.endswith("+json")
