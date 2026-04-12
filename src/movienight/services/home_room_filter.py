def proposals_for_room(
    proposals,
    room: str,
):
    return [proposal for proposal in proposals if proposal.room == room]
