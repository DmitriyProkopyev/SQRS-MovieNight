from datetime import datetime

from pydantic import BaseModel


class ProposalGroupWindow(BaseModel):
    room: str
    starts_at: datetime
    ends_at: datetime
