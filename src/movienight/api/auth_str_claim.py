from movienight.api.auth_malformed_request import raise_malformed_auth_request


def read_str_claim(payload: dict, key: str) -> str:
    value = payload.get(key)
    if isinstance(value, str):
        return value

    raise_malformed_auth_request()
