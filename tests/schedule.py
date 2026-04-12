import pytest

from datetime import UTC, date, datetime, time, timedelta
from http import HTTPStatus

from fastapi.testclient import TestClient

from movienight.db.models import Proposal, User
from movienight.db.session import SessionLocal
from movienight.core.slot_constants import ROOMS
from tests.conftest import WRONG_CONTENT_TYPES

from movienight.main import app
from movienight.db.base import Base
from movienight.db.session import engine

from tests.auth.conftest import register, login, VALID_USERNAME, VALID_PASSWORD, VALID_USERNAME_2, VALID_PASSWORD_2


SCHEDULE_ENDPOINT = "/api/v1/schedule"


@pytest.fixture(scope="function")
def client_with_logged_in_users():
    with TestClient(app, base_url="http://127.0.0.1:8000") as test_client:
        register(client=test_client, username=VALID_USERNAME, password=VALID_PASSWORD)
        register(client=test_client, username=VALID_USERNAME_2, password=VALID_PASSWORD_2)

        _, response = login(client=test_client, username=VALID_USERNAME, password=VALID_PASSWORD)
        _, response2 = login(client=test_client, username=VALID_USERNAME_2, password=VALID_PASSWORD_2)
        yield test_client, response["access_token"], response2["access_token"]

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def get_schedule(
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

    response = client.get(SCHEDULE_ENDPOINT, headers=headers)
    return response.status_code, response.json()


def create_proposal(
    username: str,
    room: str,
    movie_title: str,
    starts_at: datetime,
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


def test_valid_empty_schedule(client_with_logged_in_user) -> None:
    client, token = client_with_logged_in_user
    status_code, response = get_schedule(client=client, access_token=token)
    assert status_code == HTTPStatus.OK

    assert date.fromisoformat(response["week_end"]) == (
        date.fromisoformat(response["week_start"]) + timedelta(days=6)
    )
    assert len(response["rooms"]) == len(ROOMS)
    assert [room["room"] for room in response["rooms"]] == list(ROOMS)

    for room in response["rooms"]:
        assert len(room["slots"]) == 84
        first_slot = room["slots"][0]

        assert first_slot["room"] == room["room"]
        assert "slot_date" in first_slot
        assert "day_name" in first_slot
        assert "day_label" in first_slot
        assert "time_label" in first_slot
        assert "start_at" in first_slot
        assert "end_at" in first_slot
        assert "display_label" in first_slot
        assert first_slot["proposal_titles"] == []
        assert first_slot["proposal_count"] == 0
        assert isinstance(first_slot["is_past"], bool)
        assert isinstance(first_slot["is_locked"], bool)


def test_schedule_contains_matching_proposal(
    client_with_logged_in_user,
    monkeypatch,
) -> None:
    client, token = client_with_logged_in_user
    _, response = get_schedule(client=client, access_token=token)
    week_start = date.fromisoformat(response["week_start"])

    monkeypatch.setattr(
        "movienight.services.schedule_slot_mapper.utcnow",
        lambda: datetime.combine(week_start, time(hour=0, tzinfo=UTC)),
    )

    starts_at = datetime.combine(
        week_start + timedelta(days=2),
        time(hour=18, tzinfo=UTC),
    )
    create_proposal(
        username="MyUniqueUsername",
        room="Room B",
        movie_title="Interstellar",
        starts_at=starts_at,
    )

    status_code, response = get_schedule(client=client, access_token=token)
    assert status_code == HTTPStatus.OK

    room_schedule = next(
        room for room in response["rooms"] if room["room"] == "Room B"
    )
    slot = next(
        slot
        for slot in room_schedule["slots"]
        if slot["start_at"] == starts_at.isoformat().replace("+00:00", "Z")
    )

    assert slot["proposal_titles"] == ["Interstellar"]
    assert slot["proposal_count"] == 1
    assert slot["is_past"] is False
    assert slot["is_locked"] is False


def test_authentication_required(default_client: TestClient) -> None:
    status_code, response = get_schedule(
        client=default_client,
        access_token=None,
    )
    assert status_code == HTTPStatus.UNAUTHORIZED
    assert response["detail"] == "Authentication required."


def test_wrong_http_methods(client_with_logged_in_user) -> None:
    client, token = client_with_logged_in_user
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(SCHEDULE_ENDPOINT, headers=headers)
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    response = client.put(SCHEDULE_ENDPOINT, headers=headers)
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    response = client.patch(SCHEDULE_ENDPOINT, headers=headers)
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    response = client.delete(SCHEDULE_ENDPOINT, headers=headers)
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_wrong_accept_types_do_not_break_schedule(
    client_with_logged_in_user,
) -> None:
    client, token = client_with_logged_in_user

    for accept_type in WRONG_CONTENT_TYPES:
        status_code, response = get_schedule(
            client=client,
            access_token=token,
            accept=accept_type,
        )
        assert status_code == HTTPStatus.OK
        assert "rooms" in response
