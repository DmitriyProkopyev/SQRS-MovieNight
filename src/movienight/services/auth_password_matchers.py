import re

UPPERCASE_RE = re.compile(r"[A-Z]")
LOWERCASE_RE = re.compile(r"[a-z]")
DIGIT_RE = re.compile(r"\d")
SPECIAL_RE = re.compile(r"[^A-Za-z0-9]")


def has_uppercase(password: str) -> bool:
    return bool(UPPERCASE_RE.search(password))


def has_lowercase(password: str) -> bool:
    return bool(LOWERCASE_RE.search(password))


def has_digit(password: str) -> bool:
    return bool(DIGIT_RE.search(password))


def has_special(password: str) -> bool:
    return bool(SPECIAL_RE.search(password))
