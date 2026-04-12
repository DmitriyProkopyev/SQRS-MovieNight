from fastapi import HTTPException, Request, status

from movienight.api.json_accept import accept_allows_json
from movienight.api.json_content_type import content_type_is_json


def require_json_headers(request: Request) -> None:
    accept = request.headers.get("accept")
    content_type = request.headers.get("content-type")

    if not accept_allows_json(accept):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only application/json is supported.",
        )

    if not content_type_is_json(content_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only application/json is supported.",
        )
