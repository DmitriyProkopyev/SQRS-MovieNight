from movienight.db.base import Base
from movienight.db.session import engine


def initialize_schema() -> None:
    Base.metadata.create_all(bind=engine)
