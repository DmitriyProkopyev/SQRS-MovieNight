def build_bad_request_response() -> dict:
    return {
        "description": (
            "Bad Request. Validation failed for request path, "
            "query parameters, or body."
        ),
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "type": "string_too_short",
                            "loc": ["body", "username"],
                            "msg": (
                                "String should have at least "
                                "3 characters"
                            ),
                            "input": "",
                            "ctx": {"min_length": 3},
                        }
                    ]
                }
            }
        },
    }
