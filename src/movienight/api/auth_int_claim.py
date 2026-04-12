from movienight.api.auth_malformed_request import raise_malformed_auth_request


def read_int_claim(payload: dict, key: str) -> int:
    value = payload.get(key)
    if isinstance(value, int):
        return value

    raise_malformed_auth_request()
