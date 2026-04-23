from proxy.services.reaction_proposal_loader import require_proposal
from proxy.services.voting_rules import build_conflict_component


def build_vote_group_context(
    proposals_repo,
    votes_repo,
    proposal_id: int,
    current_user_id: int,
):
    proposal = require_proposal(proposals_repo, proposal_id)
    component = build_conflict_component(
        proposal,
        proposals_repo.list_by_room(proposal.room),
    )
    component_ids = [item.id for item in component]
    user_votes = votes_repo.get_user_votes_in_group(
        current_user_id,
        component_ids,
    )
    already_voted_for_target = votes_repo.exists_for_user_and_proposal(
        current_user_id,
        proposal_id,
    )

    return {
        "proposal": proposal,
        "component_ids": component_ids,
        "user_votes": user_votes,
        "already_voted_for_target": already_voted_for_target,
    }
