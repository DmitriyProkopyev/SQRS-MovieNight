from movienight.db.models import Proposal
from movienight.schemas.schedule import RoomSchedule
from movienight.services.schedule_slot_mapper import map_schedule_slot
from movienight.services.schedule_slot_matcher import (
    find_matching_proposals,
)


def build_room_schedule(
    room: str,
    proposals: list[Proposal],
    week_slots: list[dict],
) -> RoomSchedule:
    room_proposals = proposals_for_room(proposals, room)
    slots = [
        build_room_slot(slot, room_proposals)
        for slot in week_slots
    ]
    return RoomSchedule(room=room, slots=slots)


def proposals_for_room(
    proposals: list[Proposal],
    room: str,
) -> list[Proposal]:
    return [proposal for proposal in proposals if proposal.room == room]


def build_room_slot(
    slot: dict,
    room_proposals: list[Proposal],
):
    matching = find_matching_proposals(
        proposals=room_proposals,
        start_at=slot["start_at"],
        end_at=slot["end_at"],
    )
    proposal_titles = [proposal.movie_title for proposal in matching]
    return map_schedule_slot(slot, proposal_titles)
