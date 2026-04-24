from movienight.schemas.home import ProposalCard


def build_proposal_card(
    proposal,
    starts_at,
    ends_at,
    created_at,
    votes_count: int,
    my_vote: bool,
    is_past: bool,
    is_winner: bool,
    vote_state: dict,
    reaction_state: dict,
) -> ProposalCard:
    return ProposalCard(
        id=proposal.id,
        movie_title=proposal.movie_title,
        room=proposal.room,
        starts_at=starts_at,
        ends_at=ends_at,
        created_at=created_at,
        created_by=proposal.creator.username,
        votes_count=votes_count,
        my_vote=my_vote,
        my_reactions=reaction_state["visible_my_reactions"],
        reactions=reaction_state["visible_reactions"],
        show_reactions=reaction_state["reaction_block_active"],
        is_past=is_past,
        is_winner=is_winner,
        can_vote=vote_state["can_vote"],
        can_unvote=vote_state["can_unvote"],
        can_delete=vote_state["can_delete"],
        can_add_reaction=reaction_state["can_add_reaction"],
        can_remove_reaction=reaction_state["can_remove_reaction"],
    )
