from fastapi import HTTPException, Request, status


def _accept_allows_json(value: str | None) -> bool:
    if not value:
        return True

    accepted = []
    for part in value.split(","):
        media_type = part.split(";")[0].strip().lower()
        accepted.append(media_type)

    for media_type in accepted:
        if media_type in {"application/json", "*/*"}:
            return True
        if media_type.endswith("+json"):
            return True

    return False


def _content_type_is_json(value: str | None) -> bool:
    if not value:
        return True

    media_type = value.split(";")[0].strip().lower()
    return media_type == "application/json" or media_type.endswith("+json")


def require_json_headers(request: Request) -> None:
    accept = request.headers.get("accept")
    content_type = request.headers.get("content-type")

    if not _accept_allows_json(accept):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only application/json is supported.",
        )

    if not _content_type_is_json(content_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only application/json is supported.",
        )
