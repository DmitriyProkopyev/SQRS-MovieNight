PROPOSAL_CARD_EXAMPLE = {
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
    "reactions": {
        "pizza": 2,
        "popcorn": 1,
    },
    "show_reactions": True,
    "is_past": False,
    "is_winner": True,
    "can_vote": False,
    "can_unvote": False,
    "can_delete": False,
    "can_add_reaction": True,
    "can_remove_reaction": True,
}

PROPOSAL_GROUP_EXAMPLE = {
    "room": "Room A",
    "starts_at": "2026-04-06T18:00:00Z",
    "ends_at": "2026-04-06T20:00:00Z",
    "is_conflict": True,
    "is_locked": True,
    "winner_proposal_id": 12,
    "proposals": [],
}

HOME_PAGE_EXAMPLE = {
    "groups": [
        {
            "room": "Room A",
            "starts_at": "2026-04-06T18:00:00Z",
            "ends_at": "2026-04-06T20:00:00Z",
            "is_conflict": True,
            "is_locked": True,
            "winner_proposal_id": 12,
            "proposals": [PROPOSAL_CARD_EXAMPLE],
        }
    ]
}
