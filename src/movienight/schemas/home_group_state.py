from pydantic import BaseModel


class ProposalGroupState(BaseModel):
    is_conflict: bool
    is_locked: bool
    winner_proposal_id: int | None
