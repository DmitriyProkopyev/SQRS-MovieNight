from movienight.api.auth_positive_decimal import parse_positive_decimal
from movienight.api.auth_str_claim import read_str_claim


def read_numeric_subject(payload: dict) -> int:
    subject = read_str_claim(payload, "sub")
    return parse_positive_decimal(subject)
