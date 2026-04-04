class DomainError(Exception):
    """Business rule violation."""


class NotFoundError(DomainError):
    """Requested entity does not exist."""
