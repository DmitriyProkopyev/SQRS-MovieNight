from proxy.db.default_user_credentials import (
    get_default_user_credentials,
)
from proxy.db.default_user_factory import build_default_user
from proxy.db.default_user_lookup import default_user_exists


def ensure_default_user(db) -> None:
    credentials = get_default_user_credentials()
    if credentials is None:
        return

    username, password = credentials
    if default_user_exists(db, username):
        return

    db.add(build_default_user(username, password))
    db.commit()
