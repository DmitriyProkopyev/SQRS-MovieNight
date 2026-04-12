from movienight.db.init_default_user import ensure_default_user
from movienight.db.init_schema import initialize_schema
from movienight.db.session import SessionLocal


def initialize_database() -> None:
    initialize_schema()

    db = SessionLocal()
    try:
        ensure_default_user(db)
    finally:
        db.close()
