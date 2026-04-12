from datetime import datetime

from pydantic import BaseModel


class ProposalCardIdentity(BaseModel):
    id: int
    movie_title: str
    room: str
    starts_at: datetime
    ends_at: datetime
    created_at: datetime
    created_by: str
    votes_count: int
