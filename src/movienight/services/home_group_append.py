from movienight.services.home_group_component import build_home_component
from movienight.services.home_group_mapper import map_group
from movienight.services.home_group_visited import mark_component_visited


def append_home_group(
    groups,
    visited: set[int],
    proposals,
    proposal,
    vote_counts,
    reaction_counts,
    my_reactions_map,
    my_votes,
    current_user,
    now,
) -> None:
    component = build_home_component(proposals, proposal)
    mark_component_visited(visited, component)

    groups.append(
        map_group(
            component=component,
            vote_counts=vote_counts,
            reaction_counts=reaction_counts,
            my_reactions_map=my_reactions_map,
            my_votes=my_votes,
            current_user=current_user,
            now=now,
        )
    )
