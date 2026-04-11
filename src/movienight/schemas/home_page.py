from pydantic import BaseModel, ConfigDict

from movienight.schemas.home_examples import HOME_PAGE_EXAMPLE
from movienight.schemas.home_group import ProposalGroup


class HomePageResponse(BaseModel):
    groups: list[ProposalGroup]

    model_config = ConfigDict(
        json_schema_extra={"example": HOME_PAGE_EXAMPLE}
    )
