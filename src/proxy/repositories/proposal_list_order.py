from sqlalchemy import Select

from proxy.db.models import Proposal


def apply_proposal_order(statement: Select) -> Select:
    return statement.order_by(
        Proposal.starts_at,
        Proposal.created_at,
    )
