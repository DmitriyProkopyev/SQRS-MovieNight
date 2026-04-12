from pydantic import BaseModel


class ProposalCardFlags(BaseModel):
    show_reactions: bool
    is_past: bool
    is_winner: bool

    can_vote: bool
    can_unvote: bool
    can_delete: bool
    can_add_reaction: bool
    can_remove_reaction: bool
