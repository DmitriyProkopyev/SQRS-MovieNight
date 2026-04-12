from datetime import timedelta
from http import HTTPStatus

from fastapi.testclient import TestClient

from movienight.core.clock import utcnow
from movienight.db.models import Proposal, User
from movienight.db.session import SessionLocal
from tests.auth.conftest import (
    VALID_USERNAME,
    VALID_USERNAME_2,
    WRONG_CONTENT_TYPES,
)


CATALOG_ENDPOINT = "/api/v1/catalog"


def get_catalog(
    client: TestClient,
    access_token: str | None,
    accept: str = "application/json",
    content_type: str = "application/json",
):
    headers = {}
    if accept:
        headers["accept"] = accept
    if content_type:
        headers["Content-Type"] = content_type
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    response = client.get(CATALOG_ENDPOINT, headers=headers)
    return response.status_code, response.json()


def create_proposal(
    username: str,
    room: str,
    movie_title: str,
    starts_at,
) -> Proposal:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).one()
        proposal = Proposal(
            creator_id=user.id,
            room=room,
            movie_title=movie_title,
            starts_at=starts_at,
            ends_at=starts_at + timedelta(hours=2),
            created_at=starts_at - timedelta(days=1),
        )
        db.add(proposal)
        db.commit()
        db.refresh(proposal)
        return proposal
    finally:
        db.close()


def test_valid_empty_catalog(client_with_logged_in_user) -> None:
    client, token = client_with_logged_in_user
    status_code, response = get_catalog(client=client, access_token=token)
    assert status_code == HTTPStatus.OK
    assert response["groups"] == []


def test_catalog_returns_all_users_proposals_in_conflict_group(
    client_with_logged_in_user,
) -> None:
    client, token = client_with_logged_in_user
    starts_at = utcnow() + timedelta(days=2)
    starts_at = starts_at.replace(
        hour=18,
        minute=0,
        second=0,
        microsecond=0,
    )

    first = create_proposal(
        username=VALID_USERNAME,
        room="Room A",
        movie_title="Interstellar",
        starts_at=starts_at,
    )
    second = create_proposal(
        username=VALID_USERNAME_2,
        room="Room A",
        movie_title="The Matrix",
        starts_at=starts_at,
    )

    status_code, response = get_catalog(client=client, access_token=token)
    assert status_code == HTTPStatus.OK
    assert len(response["groups"]) == 1

    group = response["groups"][0]
    assert group["room"] == "Room A"
    assert group["is_conflict"] is True
    assert group["is_locked"] is False
    assert group["winner_proposal_id"] is None
    assert len(group["proposals"]) == 2

    cards_by_id = {
        proposal["id"]: proposal
        for proposal in group["proposals"]
    }
    assert set(cards_by_id) == {first.id, second.id}

    first_card = cards_by_id[first.id]
    second_card = cards_by_id[second.id]

    assert first_card["movie_title"] == "Interstellar"
    assert first_card["created_by"] == VALID_USERNAME
    assert first_card["room"] == "Room A"
    assert first_card["votes_count"] == 0
    assert first_card["my_vote"] is False
    assert first_card["my_reactions"] == []
    assert first_card["reactions"] is None
    assert first_card["show_reactions"] is False
    assert first_card["is_past"] is False
    assert first_card["is_winner"] is False

    assert second_card["movie_title"] == "The Matrix"
    assert second_card["created_by"] == VALID_USERNAME_2
    assert second_card["room"] == "Room A"
    assert second_card["votes_count"] == 0
    assert second_card["my_vote"] is False
    assert second_card["my_reactions"] == []
    assert second_card["reactions"] is None
    assert second_card["show_reactions"] is False
    assert second_card["is_past"] is False
    assert second_card["is_winner"] is False


def test_authentication_required(default_client: TestClient) -> None:
    status_code, response = get_catalog(
        client=default_client,
        access_token=None,
    )
    assert status_code == HTTPStatus.UNAUTHORIZED
    assert response["detail"] == "Authentication required."


def test_wrong_http_methods(client_with_logged_in_user) -> None:
    client, token = client_with_logged_in_user
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(CATALOG_ENDPOINT, headers=headers)
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    response = client.put(CATALOG_ENDPOINT, headers=headers)
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    response = client.patch(CATALOG_ENDPOINT, headers=headers)
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    response = client.delete(CATALOG_ENDPOINT, headers=headers)
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_wrong_accept_types_do_not_break_catalog(
    client_with_logged_in_user,
) -> None:
    client, token = client_with_logged_in_user

    for accept_type in WRONG_CONTENT_TYPES:
        status_code, response = get_catalog(
            client=client,
            access_token=token,
            accept=accept_type,
        )
        assert status_code == HTTPStatus.OK
        assert "groups" in response
