from pydantic import ConfigDict

from movienight.schemas.home_card import ProposalCard
from movienight.schemas.home_examples import PROPOSAL_GROUP_EXAMPLE
from movienight.schemas.home_group_state import ProposalGroupState
from movienight.schemas.home_group_window import ProposalGroupWindow


class ProposalGroup(
    ProposalGroupWindow,
    ProposalGroupState,
):
    proposals: list[ProposalCard]

    model_config = ConfigDict(
        json_schema_extra={"example": PROPOSAL_GROUP_EXAMPLE}
    )
