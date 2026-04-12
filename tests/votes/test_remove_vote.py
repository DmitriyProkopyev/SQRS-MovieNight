from datetime import timedelta
from http import HTTPStatus
from freezegun import freeze_time

from tests.proposals.conftest import create_proposal, next_suitable_timeslot
from tests.votes.conftest import add_vote, remove_vote, fresh_token, VALID_USERNAME_2, VALID_PASSWORD_2


def test_valid_vote_removal(client_with_three_logged_in_users) -> None:
    client, token1, token2, token3 = client_with_three_logged_in_users
    start, end = next_suitable_timeslot()

    _, proposal = create_proposal(
        client=client,
        access_token=token1,
        starts_at=start,
        ends_at=end,
        movie_title="The Matrix",
        room="Room A",
    )
    proposal_id = proposal["id"]

    status_code, response = add_vote(client=client, proposal_id=proposal_id, access_token=token2)
    assert status_code == HTTPStatus.CREATED
    assert response["votes_count"] == 1

    status_code, response = add_vote(client=client, proposal_id=proposal_id, access_token=token3)
    assert status_code == HTTPStatus.CREATED
    assert response["votes_count"] == 2

    status_code, response = remove_vote(client=client,proposal_id=proposal_id, access_token=token2)
    assert status_code == HTTPStatus.OK

    assert response["proposal_id"] == proposal_id
    assert response["votes_count"] == 1
    assert response["message"] == "Vote removed."


def test_removing_non_existent_vote_is_rejected(
    client_with_three_logged_in_users,
) -> None:
    client, token1, token2, _ = client_with_three_logged_in_users
    start, end = next_suitable_timeslot()

    _, proposal = create_proposal(
        client=client,
        access_token=token1,
        starts_at=start,
        ends_at=end,
        movie_title="Inception",
        room="Room A",
    )

    status_code, response = remove_vote(client=client, proposal_id=proposal["id"], access_token=token2)
    assert status_code == HTTPStatus.NOT_FOUND
    assert response["detail"] == "Vote not found."


def test_removing_vote_in_past_is_rejected(client_with_three_logged_in_users) -> None:
    client, token1, token2, _ = client_with_three_logged_in_users
    start, end = next_suitable_timeslot()

    _, proposal = create_proposal(
        client=client,
        access_token=token1,
        starts_at=start,
        ends_at=end,
        movie_title="Interstellar",
        room="Room A",
    )
    proposal_id = proposal["id"]

    status_code, _ = add_vote(client=client, proposal_id=proposal_id, access_token=token2)
    assert status_code == HTTPStatus.CREATED

    with freeze_time(start + timedelta(hours=20)):
        refreshed_token = fresh_token(client, VALID_USERNAME_2, VALID_PASSWORD_2)
        status_code, response = remove_vote(client=client, proposal_id=proposal_id, access_token=refreshed_token)

        assert status_code == HTTPStatus.BAD_REQUEST
        assert response["detail"] == "Vote cancellation is not allowed for this proposal anymore."


def test_removing_vote_in_final_hour_is_rejected(client_with_three_logged_in_users) -> None:
    client, token1, token2, _ = client_with_three_logged_in_users
    start, end = next_suitable_timeslot()

    _, proposal = create_proposal(
        client=client,
        access_token=token1,
        starts_at=start,
        ends_at=end,
        movie_title="Interstellar",
        room="Room A",
    )
    proposal_id = proposal["id"]

    status_code, _ = add_vote(client=client, proposal_id=proposal_id, access_token=token2)
    assert status_code == HTTPStatus.CREATED

    with freeze_time(start - timedelta(hours=1)):
        refreshed_token = fresh_token(client, VALID_USERNAME_2, VALID_PASSWORD_2)
        status_code, response = remove_vote(client=client, proposal_id=proposal_id, access_token=refreshed_token)

        assert status_code == HTTPStatus.BAD_REQUEST
        assert response["detail"] == "Vote cancellation is not allowed for this proposal anymore."


def test_removing_vote_after_start_is_rejected(client_with_three_logged_in_users) -> None:
    client, token1, token2, _ = client_with_three_logged_in_users
    start, end = next_suitable_timeslot()

    _, proposal = create_proposal(
        client=client,
        access_token=token1,
        starts_at=start,
        ends_at=end,
        movie_title="Interstellar",
        room="Room A",
    )
    proposal_id = proposal["id"]

    status_code, _ = add_vote(client=client, proposal_id=proposal_id, access_token=token2)
    assert status_code == HTTPStatus.CREATED

    with freeze_time(start + timedelta(minutes=1)):
        refreshed_token = fresh_token(client, VALID_USERNAME_2, VALID_PASSWORD_2)
        status_code, response = remove_vote(client=client, proposal_id=proposal_id, access_token=refreshed_token)

        assert status_code == HTTPStatus.BAD_REQUEST
        assert response["detail"] == "Vote cancellation is not allowed for this proposal anymore."


def test_removing_vote_without_auth_is_rejected(client_with_three_logged_in_users) -> None:
    client, token1, token2, _ = client_with_three_logged_in_users
    start, end = next_suitable_timeslot()

    _, proposal = create_proposal(
        client=client,
        access_token=token1,
        starts_at=start,
        ends_at=end,
        movie_title="Arrival",
        room="Room A",
    )
    proposal_id = proposal["id"]

    status_code, _ = add_vote(client=client, proposal_id=proposal_id, access_token=token2)
    assert status_code == HTTPStatus.CREATED

    status_code, response = remove_vote(client=client, proposal_id=proposal_id, access_token=None)
    assert status_code == HTTPStatus.UNAUTHORIZED
    assert response["detail"] == "Authentication required."
