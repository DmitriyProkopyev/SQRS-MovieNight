from movienight.db.models import Proposal, User


def build_vote_state(
    proposal: Proposal,
    current_user: User,
    my_vote: bool,
    vote_locked: bool,
    is_past: bool,
) -> dict[str, bool]:
    is_owner = proposal.creator_id == current_user.id

    return {
        "can_vote": not any(
            (my_vote, is_owner, vote_locked, is_past)
        ),
        "can_unvote": my_vote and not vote_locked and not is_past,
        "can_delete": is_owner and not is_past,
    }
