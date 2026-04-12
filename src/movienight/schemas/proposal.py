from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateProposalRequest(BaseModel):
    room: str = Field(min_length=1, max_length=100)
    movie_title: str = Field(min_length=1)
    starts_at: datetime
    ends_at: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "room": "Room A",
                "movie_title": "Interstellar",
                "starts_at": "2026-04-06T18:00:00Z",
                "ends_at": "2026-04-06T20:00:00Z",
            }
        }
    )


class ProposalResponse(BaseModel):
    id: int
    room: str
    movie_title: str
    starts_at: datetime
    ends_at: datetime
    creator_id: int

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 12,
                "room": "Room A",
                "movie_title": "Interstellar",
                "starts_at": "2026-04-06T18:00:00Z",
                "ends_at": "2026-04-06T20:00:00Z",
                "creator_id": 1,
            }
        },
    )
