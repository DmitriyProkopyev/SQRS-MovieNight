from datetime import datetime

from sqlalchemy.orm import Session

from movienight.core.clock import as_utc, utcnow
from movienight.db.models import Proposal, User
from movienight.repositories.proposals import ProposalRepository
from movienight.repositories.reactions import ReactionRepository
from movienight.repositories.votes import VoteRepository
from movienight.schemas.home import (
    HomePageResponse,
    ProposalCard,
    ProposalGroup
)
from movienight.services.schedule_rules import is_in_past, is_vote_locked
from movienight.services.voting_rules import (
    build_conflict_component,
    choose_winner,
    is_reaction_target,
)


class HomeService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.proposals = ProposalRepository(db)
        self.votes = VoteRepository(db)
        self.reactions = ReactionRepository(db)

    def get_home_page(
        self,
        current_user: User,
        mine_only: bool = False
    ) -> HomePageResponse:
        now = utcnow()

        if mine_only:
            proposals = self.proposals.list_by_creator_id(current_user.id)
        else:
            proposals = self.proposals.list_all()

        proposal_ids = [item.id for item in proposals]

        vote_counts = self.votes.count_by_proposal_ids(proposal_ids)
        reaction_counts = self.reactions.counts_for_proposal_ids(proposal_ids)
        my_reactions_map = self.reactions.user_categories_for_proposal_ids(
            current_user.id,
            proposal_ids,
        )
        my_votes = {
            item.proposal_id
            for item in self.votes.get_user_votes_in_group(
                current_user.id,
                proposal_ids
            )
        }

        groups = self._build_groups(
            proposals=proposals,
            vote_counts=vote_counts,
            reaction_counts=reaction_counts,
            my_reactions_map=my_reactions_map,
            my_votes=my_votes,
            current_user=current_user,
            now=now,
        )
        return HomePageResponse(groups=groups)

    def _build_groups(
        self,
        proposals: list[Proposal],
        vote_counts: dict[int, int],
        reaction_counts: dict[int, dict[str, int]],
        my_reactions_map: dict[int, list[str]],
        my_votes: set[int],
        current_user: User,
        now: datetime,
    ) -> list[ProposalGroup]:
        groups: list[ProposalGroup] = []
        visited: set[int] = set()

        for proposal in proposals:
            if proposal.id in visited:
                continue

            room_proposals = [
                item for item in proposals
                if item.room == proposal.room
            ]
            component = build_conflict_component(
                proposal,
                room_proposals
            )
            visited.update(item.id for item in component)

            groups.append(
                self._to_group(
                    component=component,
                    vote_counts=vote_counts,
                    reaction_counts=reaction_counts,
                    my_reactions_map=my_reactions_map,
                    my_votes=my_votes,
                    current_user=current_user,
                    now=now,
                )
            )

        groups.sort(
            key=lambda group: (
                group.starts_at,
                group.room
            )
        )
        return groups

    def _to_group(
        self,
        component: list[Proposal],
        vote_counts: dict[int, int],
        reaction_counts: dict[int, dict[str, int]],
        my_reactions_map: dict[int, list[str]],
        my_votes: set[int],
        current_user: User,
        now: datetime,
    ) -> ProposalGroup:
        winner = choose_winner(
            component,
            vote_counts,
        ) if component else None

        group_starts_at = min(as_utc(item.starts_at) for item in component)
        group_ends_at = max(as_utc(item.ends_at) for item in component)
        group_is_locked = is_vote_locked(group_starts_at, now)
        show_winner = len(component) > 1 and group_is_locked
        winner_id = winner.id if winner and show_winner else None

        component_vote_counts = {
            item.id: vote_counts.get(item.id, 0)
            for item in component
        }

        cards = [
            self._to_card(
                proposal=item,
                component=component,
                component_vote_counts=component_vote_counts,
                votes_count=vote_counts.get(item.id, 0),
                my_vote=item.id in my_votes,
                reactions=reaction_counts.get(item.id, {}),
                my_reactions=my_reactions_map.get(item.id, []),
                current_user=current_user,
                now=now,
                winner_id=winner_id,
            )
            for item in component
        ]

        return ProposalGroup(
            room=component[0].room,
            starts_at=group_starts_at,
            ends_at=group_ends_at,
            is_conflict=len(component) > 1,
            is_locked=group_is_locked,
            winner_proposal_id=winner_id,
            proposals=cards,
        )

    def _to_card(
        self,
        proposal: Proposal,
        component: list[Proposal],
        component_vote_counts: dict[int, int],
        votes_count: int,
        my_vote: bool,
        reactions: dict[str, int],
        my_reactions: list[str],
        current_user: User,
        now: datetime,
        winner_id: int | None,
    ) -> ProposalCard:
        starts_at, ends_at, created_at, now = self._normalize_card_times(
            proposal=proposal,
            now=now,
        )

        is_past = is_in_past(starts_at, now)
        vote_locked = is_vote_locked(starts_at, now)

        (
            reaction_block_active,
            visible_reactions,
            visible_my_reactions,
            can_add_reaction,
            can_remove_reaction,
        ) = self._build_reaction_state(
            proposal=proposal,
            component=component,
            component_vote_counts=component_vote_counts,
            reactions=reactions,
            my_reactions=my_reactions,
            now=now,
        )

        can_vote, can_unvote, can_delete = self._build_vote_state(
            proposal=proposal,
            current_user=current_user,
            my_vote=my_vote,
            vote_locked=vote_locked,
            is_past=is_past,
        )
        return ProposalCard(
            id=proposal.id,
            movie_title=proposal.movie_title,
            room=proposal.room,
            starts_at=starts_at,
            ends_at=ends_at,
            created_at=created_at,
            created_by=proposal.creator.username,
            votes_count=votes_count,
            my_vote=my_vote,
            my_reactions=visible_my_reactions,
            reactions=visible_reactions,
            show_reactions=reaction_block_active,
            is_past=is_past,
            is_winner=self._is_winner(proposal.id, winner_id),
            can_vote=can_vote,
            can_unvote=can_unvote,
            can_delete=can_delete,
            can_add_reaction=can_add_reaction,
            can_remove_reaction=can_remove_reaction,
        )

    def _normalize_card_times(
        self,
        proposal: Proposal,
        now: datetime,
    ) -> tuple[datetime, datetime, datetime, datetime]:
        starts_at = as_utc(proposal.starts_at)
        ends_at = as_utc(proposal.ends_at)
        created_at = as_utc(proposal.created_at)
        normalized_now = as_utc(now)
        return starts_at, ends_at, created_at, normalized_now

    def _build_vote_state(
        self,
        proposal: Proposal,
        current_user: User,
        my_vote: bool,
        vote_locked: bool,
        is_past: bool,
    ) -> tuple[bool, bool, bool]:
        is_owner = proposal.creator_id == current_user.id

        can_vote = not any((
            my_vote,
            is_owner,
            vote_locked,
            is_past,
        ))
        can_unvote = my_vote and not vote_locked and not is_past
        can_delete = is_owner and not is_past

        return can_vote, can_unvote, can_delete

    def _build_reaction_state(
        self,
        proposal: Proposal,
        component: list[Proposal],
        component_vote_counts: dict[int, int],
        reactions: dict[str, int],
        my_reactions: list[str],
        now: datetime,
    ) -> tuple[bool, dict[str, int] | None, list[str], bool, bool]:
        reaction_block_active = is_reaction_target(
            proposal=proposal,
            component=component,
            vote_counts=component_vote_counts,
            now=now,
        )

        if reaction_block_active:
            visible_reactions: dict[str, int] | None = reactions
            visible_my_reactions = my_reactions
        else:
            visible_reactions = None
            visible_my_reactions = []

        can_add_reaction = reaction_block_active
        can_remove_reaction = reaction_block_active and bool(my_reactions)

        return (
            reaction_block_active,
            visible_reactions,
            visible_my_reactions,
            can_add_reaction,
            can_remove_reaction,
        )

    def _is_winner(self, proposal_id: int, winner_id: int | None) -> bool:
        return winner_id is not None and winner_id == proposal_id
