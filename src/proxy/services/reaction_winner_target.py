from proxy.services.voting_winner_selector import choose_winner


def matches_reaction_target(
    proposal,
    component,
    vote_counts: dict[int, int],
) -> bool:
    if len(component) == 1:
        return True

    winner = choose_winner(component, vote_counts)
    return proposal.id == winner.id
