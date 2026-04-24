from proxy.services.home_group_append import append_home_group
from proxy.services.home_group_skip import should_skip_group_proposal


def accumulate_home_groups(
    proposals,
    vote_counts,
    reaction_counts,
    my_reactions_map,
    my_votes,
    current_user,
    now,
):
    groups = []
    visited: set[int] = set()

    for proposal in proposals:
        if should_skip_group_proposal(proposal.id, visited):
            continue

        append_home_group(
            groups=groups,
            visited=visited,
            proposals=proposals,
            proposal=proposal,
            vote_counts=vote_counts,
            reaction_counts=reaction_counts,
            my_reactions_map=my_reactions_map,
            my_votes=my_votes,
            current_user=current_user,
            now=now,
        )

    return groups
