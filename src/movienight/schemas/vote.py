from pydantic import BaseModel, ConfigDict


class VoteActionResponse(BaseModel):
    proposal_id: int
    votes_count: int
    message: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "proposal_id": 12,
                "votes_count": 3,
                "message": "Vote added.",
            }
        }
    )
