from datetime import datetime, timedelta
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from freezegun import freeze_time

from movienight.db.base import Base
from movienight.db.session import engine
from movienight.main import app
from tests.auth.conftest import (
    VALID_PASSWORD,
    VALID_PASSWORD_2,
    VALID_USERNAME,
    VALID_USERNAME_2,
    login,
    register,
)
from tests.proposals.conftest import create_proposal, next_suitable_timeslot

VOTE_ENDPOINT_TEMPLATE = "/api/v1/proposals/{proposal_id}/votes"

VALID_USERNAME_3 = "ThirdValidUser"
VALID_PASSWORD_3 = "G00d!Password_3"


def add_vote(
    client: TestClient,
    proposal_id: int,
    access_token: str | None,
):
    headers = {"accept": "application/json"}
    if access_token is not None:
        headers["Authorization"] = f"Bearer {access_token}"

    response = client.post(
        VOTE_ENDPOINT_TEMPLATE.format(proposal_id=proposal_id),
        headers=headers,
    )
    return response.status_code, response.json()

def remove_vote(
    client: TestClient,
    proposal_id: int,
    access_token: str | None,
):
    headers = {"accept": "application/json"}
    if access_token is not None:
        headers["Authorization"] = f"Bearer {access_token}"

    response = client.delete(
        VOTE_ENDPOINT_TEMPLATE.format(proposal_id=proposal_id),
        headers=headers,
    )
    return response.status_code, response.json()

def fresh_token(
    client: TestClient,
    username: str,
    password: str,
) -> str:
    _, response = login(client=client, username=username, password=password)
    return response["access_token"]


@pytest.fixture(scope="function")
def client_with_three_logged_in_users():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestClient(app, base_url="http://127.0.0.1:8000") as test_client:
        register(
            client=test_client,
            username=VALID_USERNAME,
            password=VALID_PASSWORD,
        )
        register(
            client=test_client,
            username=VALID_USERNAME_2,
            password=VALID_PASSWORD_2,
        )
        register(
            client=test_client,
            username=VALID_USERNAME_3,
            password=VALID_PASSWORD_3,
        )

        token_1 = fresh_token(
            test_client,
            VALID_USERNAME,
            VALID_PASSWORD,
        )
        token_2 = fresh_token(
            test_client,
            VALID_USERNAME_2,
            VALID_PASSWORD_2,
        )
        token_3 = fresh_token(
            test_client,
            VALID_USERNAME_3,
            VALID_PASSWORD_3,
        )

        yield test_client, token_1, token_2, token_3

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_valid_vote_and_counter_growth(
    client_with_three_logged_in_users,
) -> None:
    client, token_1, token_2, token_3 = client_with_three_logged_in_users
    start, end = next_suitable_timeslot()

    _, proposal = create_proposal(
        client=client,
        access_token=token_1,
        starts_at=start,
        ends_at=end,
        movie_title="Interstellar",
        room="Room A",
    )
    proposal_id = proposal["id"]

    status_code, response = add_vote(
        client=client,
        proposal_id=proposal_id,
        access_token=token_2,
    )
    assert status_code == HTTPStatus.CREATED
    assert response["proposal_id"] == proposal_id
    assert response["votes_count"] == 1
    assert response["message"] == "Vote added."

    status_code, response = add_vote(
        client=client,
        proposal_id=proposal_id,
        access_token=token_3,
    )
    assert status_code == HTTPStatus.CREATED
    assert response["proposal_id"] == proposal_id
    assert response["votes_count"] == 2
    assert response["message"] == "Vote added."


def test_vote_for_own_proposal_is_rejected(
    client_with_three_logged_in_users,
) -> None:
    client, token_1, _, _ = client_with_three_logged_in_users
    start, end = next_suitable_timeslot()

    _, proposal = create_proposal(
        client=client,
        access_token=token_1,
        starts_at=start,
        ends_at=end,
        movie_title="Blade Runner 2049",
        room="Room A",
    )

    status_code, response = add_vote(
        client=client,
        proposal_id=proposal["id"],
        access_token=token_1,
    )
    assert status_code == HTTPStatus.BAD_REQUEST
    assert response["detail"] == "You cannot vote for your own proposal."


def test_duplicate_vote_for_same_proposal_is_rejected(
    client_with_three_logged_in_users,
) -> None:
    client, token_1, token_2, _ = client_with_three_logged_in_users
    start, end = next_suitable_timeslot()

    _, proposal = create_proposal(
        client=client,
        access_token=token_1,
        starts_at=start,
        ends_at=end,
        movie_title="Dune",
        room="Room A",
    )
    proposal_id = proposal["id"]

    status_code, _ = add_vote(
        client=client,
        proposal_id=proposal_id,
        access_token=token_2,
    )
    assert status_code == HTTPStatus.CREATED

    status_code, response = add_vote(
        client=client,
        proposal_id=proposal_id,
        access_token=token_2,
    )
    assert status_code == HTTPStatus.BAD_REQUEST
    assert response["detail"] == "You have already voted for this proposal."


def test_vote_for_other_proposal_in_same_group_is_rejected(
    client_with_three_logged_in_users,
) -> None:
    client, token_1, token_2, token_3 = client_with_three_logged_in_users
    start, end = next_suitable_timeslot()

    _, proposal_1 = create_proposal(
        client=client,
        access_token=token_1,
        starts_at=start,
        ends_at=end,
        movie_title="Alien",
        room="Room A",
    )
    _, proposal_2 = create_proposal(
        client=client,
        access_token=token_3,
        starts_at=start,
        ends_at=end,
        movie_title="Arrival",
        room="Room A",
    )

    status_code, _ = add_vote(
        client=client,
        proposal_id=proposal_1["id"],
        access_token=token_2,
    )
    assert status_code == HTTPStatus.CREATED

    status_code, response = add_vote(
        client=client,
        proposal_id=proposal_2["id"],
        access_token=token_2,
    )
    assert status_code == HTTPStatus.BAD_REQUEST
    assert response["detail"] == "You have already voted in this voting group."


def test_vote_is_rejected_in_final_hour_and_in_past(
    client_with_three_logged_in_users,
) -> None:
    client, token_1, _, _ = client_with_three_logged_in_users
    start, end = next_suitable_timeslot()

    _, proposal = create_proposal(
        client=client,
        access_token=token_1,
        starts_at=start,
        ends_at=end,
        movie_title="Tenet",
        room="Room A",
    )
    proposal_id = proposal["id"]

    with freeze_time(start - timedelta(hours=1)):
        token_2 = fresh_token(
            client,
            VALID_USERNAME_2,
            VALID_PASSWORD_2,
        )
        status_code, response = add_vote(
            client=client,
            proposal_id=proposal_id,
            access_token=token_2,
        )
        assert status_code == HTTPStatus.BAD_REQUEST
        assert response["detail"] == (
            "Voting is not allowed for this proposal anymore."
        )

    with freeze_time(start + timedelta(minutes=1)):
        token_2 = fresh_token(
            client,
            VALID_USERNAME_2,
            VALID_PASSWORD_2,
        )
        status_code, response = add_vote(
            client=client,
            proposal_id=proposal_id,
            access_token=token_2,
        )
        assert status_code == HTTPStatus.BAD_REQUEST
        assert response["detail"] == (
            "Voting is not allowed for this proposal anymore."
        )


def test_vote_for_missing_proposal_and_without_auth_is_rejected(
    client_with_three_logged_in_users,
) -> None:
    client, _, token_2, _ = client_with_three_logged_in_users

    status_code, response = add_vote(
        client=client,
        proposal_id=999999,
        access_token=token_2,
    )
    assert status_code == HTTPStatus.NOT_FOUND
    assert response["detail"] == "Proposal not found."

    status_code, response = add_vote(
        client=client,
        proposal_id=999999,
        access_token=None,
    )
    assert status_code == HTTPStatus.UNAUTHORIZED
    assert response["detail"] == "Authentication required."

def test_valid_remove_vote_and_counter_decrease(
    client_with_three_logged_in_users,
) -> None:
    client, token_1, token_2, token_3 = client_with_three_logged_in_users
    start, end = next_suitable_timeslot()

    _, proposal = create_proposal(
        client=client,
        access_token=token_1,
        starts_at=start,
        ends_at=end,
        movie_title="The Matrix",
        room="Room A",
    )
    proposal_id = proposal["id"]

    status_code, response = add_vote(
        client=client,
        proposal_id=proposal_id,
        access_token=token_2,
    )
    assert status_code == HTTPStatus.CREATED
    assert response["votes_count"] == 1

    status_code, response = add_vote(
        client=client,
        proposal_id=proposal_id,
        access_token=token_3,
    )
    assert status_code == HTTPStatus.CREATED
    assert response["votes_count"] == 2

    status_code, response = remove_vote(
        client=client,
        proposal_id=proposal_id,
        access_token=token_2,
    )
    assert status_code == HTTPStatus.OK
    assert response["proposal_id"] == proposal_id
    assert response["votes_count"] == 1
    assert response["message"] == "Vote removed."


def test_remove_vote_without_existing_vote_is_rejected(
    client_with_three_logged_in_users,
) -> None:
    client, token_1, token_2, _ = client_with_three_logged_in_users
    start, end = next_suitable_timeslot()

    _, proposal = create_proposal(
        client=client,
        access_token=token_1,
        starts_at=start,
        ends_at=end,
        movie_title="Inception",
        room="Room A",
    )

    status_code, response = remove_vote(
        client=client,
        proposal_id=proposal["id"],
        access_token=token_2,
    )
    assert status_code == HTTPStatus.BAD_REQUEST
    assert "detail" in response
    assert response["detail"] == "No vote to remove."


def test_remove_vote_is_rejected_in_final_hour_and_after_start(
    client_with_three_logged_in_users,
) -> None:
    client, token_1, token_2, _ = client_with_three_logged_in_users
    start, end = next_suitable_timeslot()

    _, proposal = create_proposal(
        client=client,
        access_token=token_1,
        starts_at=start,
        ends_at=end,
        movie_title="Interstellar",
        room="Room A",
    )
    proposal_id = proposal["id"]

    status_code, _ = add_vote(
        client=client,
        proposal_id=proposal_id,
        access_token=token_2,
    )
    assert status_code == HTTPStatus.CREATED

    with freeze_time(start - timedelta(hours=1)):
        refreshed_token = fresh_token(
            client,
            VALID_USERNAME_2,
            VALID_PASSWORD_2,
        )
        status_code, response = remove_vote(
            client=client,
            proposal_id=proposal_id,
            access_token=refreshed_token,
        )
        assert status_code == HTTPStatus.BAD_REQUEST
        assert "detail" in response
        assert response["detail"] == (
            "Vote cancellation is not allowed for this proposal anymore."
        )

    with freeze_time(start + timedelta(minutes=1)):
        refreshed_token = fresh_token(
            client,
            VALID_USERNAME_2,
            VALID_PASSWORD_2,
        )
        status_code, response = remove_vote(
            client=client,
            proposal_id=proposal_id,
            access_token=refreshed_token,
        )
        assert status_code == HTTPStatus.BAD_REQUEST
        assert "detail" in response
        assert response["detail"] == (
            "Vote cancellation is not allowed for this proposal anymore."
        )


def test_remove_vote_without_auth_is_rejected(
    client_with_three_logged_in_users,
) -> None:
    client, token_1, token_2, _ = client_with_three_logged_in_users
    start, end = next_suitable_timeslot()

    _, proposal = create_proposal(
        client=client,
        access_token=token_1,
        starts_at=start,
        ends_at=end,
        movie_title="Arrival",
        room="Room A",
    )
    proposal_id = proposal["id"]

    status_code, _ = add_vote(
        client=client,
        proposal_id=proposal_id,
        access_token=token_2,
    )
    assert status_code == HTTPStatus.CREATED

    status_code, response = remove_vote(
        client=client,
        proposal_id=proposal_id,
        access_token=None,
    )
    assert status_code == HTTPStatus.UNAUTHORIZED
    assert "detail" in response
    assert response["detail"] == "Authentication required."