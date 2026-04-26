import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from proxy.connection_provider import EncryptedSQLiteClient

SQLITE_DB_PATH = os.environ.get("SQLITE_DB_PATH", "data/movienight.db")

_sqlite_client = EncryptedSQLiteClient(db_path=SQLITE_DB_PATH)

engine = create_engine(
    "sqlite://",
    creator=_sqlite_client.connect,
    poolclass=NullPool,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    class_=Session,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()