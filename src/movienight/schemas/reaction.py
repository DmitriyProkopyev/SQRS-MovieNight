from pydantic import BaseModel, ConfigDict, Field


class AddReactionRequest(BaseModel):
    category: str = Field(min_length=1, max_length=50)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "category": "pizza"
            }
        }
    )


class ReactionActionResponse(BaseModel):
    proposal_id: int
    category: str
    total_for_category: int
    message: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "proposal_id": 12,
                "category": "pizza",
                "total_for_category": 2,
                "message": "Reaction added.",
            }
        }
    )