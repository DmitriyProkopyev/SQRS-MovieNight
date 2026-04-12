from sqlalchemy.orm import Session


def create_user(
    db: Session,
    user,
):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
