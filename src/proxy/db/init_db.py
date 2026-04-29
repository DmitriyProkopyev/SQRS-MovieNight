from proxy.db.init_default_user import ensure_default_user
from proxy.db.init_schema import initialize_schema
from proxy.db.session import SessionLocal
from proxy.connection_provider import init_encryption_key


def initialize_database() -> None:
    init_encryption_key()
    initialize_schema()
    db = SessionLocal()
    try:
        ensure_default_user(db)
    finally:
        db.close()