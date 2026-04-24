from proxy.db.models import User


def default_user_exists(
    db,
    username: str,
) -> bool:
    existing_user = db.query(User).filter(
        User.username == username
    ).first()
    return existing_user is not None
