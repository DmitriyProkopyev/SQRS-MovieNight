from pydantic import ConfigDict

from movienight.schemas.home_card_flags import ProposalCardFlags
from movienight.schemas.home_card_identity import ProposalCardIdentity
from movienight.schemas.home_card_user_state import ProposalCardUserState
from movienight.schemas.home_examples import PROPOSAL_CARD_EXAMPLE


class ProposalCard(
    ProposalCardIdentity,
    ProposalCardUserState,
    ProposalCardFlags,
):
    model_config = ConfigDict(
        json_schema_extra={"example": PROPOSAL_CARD_EXAMPLE}
    )
