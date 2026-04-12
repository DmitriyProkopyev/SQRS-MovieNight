from sqlalchemy import delete
from sqlalchemy.orm import Session

from movienight.db.models import FoodReaction


def create_reaction(
    db: Session,
    reaction: FoodReaction,
) -> None:
    db.add(reaction)
    db.commit()


def delete_reaction(
    db: Session,
    reaction: FoodReaction,
) -> None:
    db.execute(
        delete(FoodReaction).where(
            FoodReaction.id == reaction.id,
        )
    )
    db.commit()
