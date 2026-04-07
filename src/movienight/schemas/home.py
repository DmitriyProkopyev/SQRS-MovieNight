from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProposalCard(BaseModel):
    id: int
    movie_title: str
    room: str
    starts_at: datetime
    ends_at: datetime
    created_at: datetime
    created_by: str
    votes_count: int

    my_vote: bool
    my_reactions: list[str]
    reactions: dict[str, int] | None

    show_reactions: bool
    is_past: bool
    is_winner: bool

    can_vote: bool
    can_unvote: bool
    can_delete: bool
    can_add_reaction: bool
    can_remove_reaction: bool

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 12,
                "movie_title": "Interstellar",
                "room": "Room A",
                "starts_at": "2026-04-06T18:00:00Z",
                "ends_at": "2026-04-06T20:00:00Z",
                "created_at": "2026-04-04T10:15:00Z",
                "created_by": "admin",
                "votes_count": 3,
                "my_vote": False,
                "my_reactions": ["pizza"],
                "reactions": {"pizza": 2, "popcorn": 1},
                "show_reactions": True,
                "is_past": False,
                "is_winner": True,
                "can_vote": False,
                "can_unvote": False,
                "can_delete": False,
                "can_add_reaction": True,
                "can_remove_reaction": True,
            }
        }
    )


class ProposalGroup(BaseModel):
    room: str
    starts_at: datetime
    ends_at: datetime
    is_conflict: bool
    is_locked: bool
    winner_proposal_id: int | None
    proposals: list[ProposalCard]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "room": "Room A",
                "starts_at": "2026-04-06T18:00:00Z",
                "ends_at": "2026-04-06T20:00:00Z",
                "is_conflict": True,
                "is_locked": True,
                "winner_proposal_id": 12,
                "proposals": [],
            }
        }
    )


class HomePageResponse(BaseModel):
    groups: list[ProposalGroup]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "groups": [
                    {
                        "room": "Room A",
                        "starts_at": "2026-04-06T18:00:00Z",
                        "ends_at": "2026-04-06T20:00:00Z",
                        "is_conflict": True,
                        "is_locked": True,
                        "winner_proposal_id": 12,
                        "proposals": [
                            {
                                "id": 12,
                                "movie_title": "Interstellar",
                                "room": "Room A",
                                "starts_at": "2026-04-06T18:00:00Z",
                                "ends_at": "2026-04-06T20:00:00Z",
                                "created_at": "2026-04-04T10:15:00Z",
                                "created_by": "admin",
                                "votes_count": 3,
                                "my_vote": False,
                                "my_reactions": ["pizza"],
                                "reactions": {"pizza": 2, "popcorn": 1},
                                "show_reactions": True,
                                "is_past": False,
                                "is_winner": True,
                                "can_vote": False,
                                "can_unvote": False,
                                "can_delete": False,
                                "can_add_reaction": True,
                                "can_remove_reaction": True,
                            }
                        ],
                    }
                ]
            }
        }
    )