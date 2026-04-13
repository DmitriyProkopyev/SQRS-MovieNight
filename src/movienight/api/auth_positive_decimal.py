from movienight.api.auth_malformed_request import raise_malformed_auth_request


def parse_positive_decimal(value: str) -> int:
    if not value.isdecimal():
        raise_malformed_auth_request()

    parsed = int(value)
    if parsed > 0:
        return parsed

    raise_malformed_auth_request()
