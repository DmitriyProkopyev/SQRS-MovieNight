from movienight.api.openapi_bad_request_response import (
    build_bad_request_response,
)


def patch_operation_responses(operation: dict) -> None:
    responses = operation.get("responses", {})
    if "422" not in responses:
        return

    responses.pop("422")
    if "400" in responses:
        return

    responses["400"] = build_bad_request_response()
