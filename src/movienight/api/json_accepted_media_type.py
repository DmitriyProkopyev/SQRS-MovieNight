def accepts_json_media_type(media_type: str) -> bool:
    if media_type in {"application/json", "*/*"}:
        return True

    return media_type.endswith("+json")
