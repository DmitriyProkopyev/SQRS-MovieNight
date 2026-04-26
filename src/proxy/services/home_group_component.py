from proxy.services.home_room_filter import proposals_for_room
from proxy.services.voting_rules import build_conflict_component


def build_home_component(
    proposals,
    proposal,
):
    return build_conflict_component(
        proposal,
        proposals_for_room(proposals, proposal.room),
    )
