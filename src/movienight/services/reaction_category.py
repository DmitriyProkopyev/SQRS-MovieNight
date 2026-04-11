from fastapi import HTTPException, status

from movienight.db.models import FoodCategory


def normalize_category(category: str) -> str:
    value = category.strip().lower()

    try:
        return FoodCategory(value).value
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unknown food reaction category.",
        ) from exc
