def normalize_media_type(value: str) -> str:
    return value.split(";")[0].strip().lower()
