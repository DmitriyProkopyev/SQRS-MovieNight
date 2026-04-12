from typing import Annotated, Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from movienight.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbSession = Annotated[Session, Depends(get_db)]
