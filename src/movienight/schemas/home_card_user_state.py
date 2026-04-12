from pydantic import BaseModel


class ProposalCardUserState(BaseModel):
    my_vote: bool
    my_reactions: list[str]
    reactions: dict[str, int] | None
