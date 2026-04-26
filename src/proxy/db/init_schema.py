from proxy.db.base import Base
from proxy.db.session import engine


def initialize_schema() -> None:
    Base.metadata.create_all(bind=engine)