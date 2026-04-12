from datetime import timedelta
from http import HTTPStatus
from freezegun import freeze_time

from tests.proposals.conftest import create_proposal, next_suitable_timeslot
from tests.votes.conftest import add_vote, fresh_token, VALID_USERNAME_2, VALID_PASSWORD_2


def test_valid_vote_and_counter_growth(client_with_three_logged_in_users) -> None:
    client, token1, token2, token3 = client_with_three_logged_in_users
    start, end = next_suitable_timeslot()

    status_code, proposal = create_proposal(
        client=client,
        access_token=token1,
        starts_at=start,
        ends_at=end,
        movie_title="Interstellar",
        room="Room A",
    )

    proposal_id = proposal["id"]
    status_code, response = add_vote(client=client, proposal_id=proposal_id, access_token=token2)
    assert status_code == HTTPStatus.CREATED

    assert response["proposal_id"] == proposal_id
    assert response["votes_count"] == 1
    assert response["message"] == "Vote added."

    status_code, response = add_vote(client=client, proposal_id=proposal_id, access_token=token3)
    assert status_code == HTTPStatus.CREATED
    assert response["proposal_id"] == proposal_id
    assert response["votes_count"] == 2
    assert response["message"] == "Vote added."


def test_vote_for_own_proposal_is_rejected(client_with_three_logged_in_users) -> None:
    client, token1, _, _ = client_with_three_logged_in_users
    start, end = next_suitable_timeslot()

    _, proposal = create_proposal(
        client=client,
        access_token=token1,
        starts_at=start,
        ends_at=end,
        movie_title="Blade Runner 2049",
        room="Room A",
    )

    status_code, response = add_vote(client=client, proposal_id=proposal["id"], access_token=token1)
    assert status_code == HTTPStatus.BAD_REQUEST
    assert response["detail"] == "You cannot vote for your own proposal."


def test_duplicate_vote_for_same_proposal_is_rejected(client_with_three_logged_in_users) -> None:
    client, token1, token2, _ = client_with_three_logged_in_users
    start, end = next_suitable_timeslot()

    _, proposal = create_proposal(
        client=client,
        access_token=token1,
        starts_at=start,
        ends_at=end,
        movie_title="Dune",
        room="Room A",
    )
    proposal_id = proposal["id"]

    status_code, _ = add_vote(client=client, proposal_id=proposal_id, access_token=token2)
    assert status_code == HTTPStatus.CREATED

    status_code, response = add_vote(client=client, proposal_id=proposal_id, access_token=token2)
    assert status_code == HTTPStatus.BAD_REQUEST
    assert response["detail"] == "You have already voted for this proposal."


def test_vote_for_other_proposal_in_same_group_is_rejected(client_with_three_logged_in_users) -> None:
    client, token1, token2, token3 = client_with_three_logged_in_users
    start, end = next_suitable_timeslot()

    _, proposal_1 = create_proposal(
        client=client,
        access_token=token1,
        starts_at=start,
        ends_at=end,
        movie_title="Alien",
        room="Room A",
    )
    _, proposal_2 = create_proposal(
        client=client,
        access_token=token3,
        starts_at=start,
        ends_at=end,
        movie_title="Arrival",
        room="Room A",
    )

    status_code, _ = add_vote(client=client, proposal_id=proposal_1["id"], access_token=token2)
    assert status_code == HTTPStatus.CREATED

    status_code, response = add_vote(client=client, proposal_id=proposal_2["id"], access_token=token2)
    assert status_code == HTTPStatus.BAD_REQUEST
    assert response["detail"] == "You have already voted in this voting group."


def test_vote_is_rejected_in_past(client_with_three_logged_in_users) -> None:
    client, token1, _, _ = client_with_three_logged_in_users
    start, end = next_suitable_timeslot()

    _, proposal = create_proposal(
        client=client,
        access_token=token1,
        starts_at=start,
        ends_at=end,
        movie_title="Tenet",
        room="Room A",
    )
    proposal_id = proposal["id"]

    with freeze_time(start + timedelta(minutes=1)):
        token2 = fresh_token(client, VALID_USERNAME_2, VALID_PASSWORD_2)
        status_code, response = add_vote(client=client, proposal_id=proposal_id, access_token=token2)
        assert status_code == HTTPStatus.BAD_REQUEST
        assert response["detail"] == "Voting is not allowed for this proposal anymore."


def test_vote_is_rejected_in_final_hour(client_with_three_logged_in_users) -> None:
    client, token1, _, _ = client_with_three_logged_in_users
    start, end = next_suitable_timeslot()

    _, proposal = create_proposal(
        client=client,
        access_token=token1,
        starts_at=start,
        ends_at=end,
        movie_title="Tenet",
        room="Room A",
    )
    proposal_id = proposal["id"]

    with freeze_time(start - timedelta(hours=1)):
        token2 = fresh_token(client, VALID_USERNAME_2, VALID_PASSWORD_2)
        status_code, response = add_vote(client=client, proposal_id=proposal_id, access_token=token2)
        assert status_code == HTTPStatus.BAD_REQUEST
        assert response["detail"] == "Voting is not allowed for this proposal anymore."


def test_vote_is_rejected_after_start(client_with_three_logged_in_users) -> None:
    client, token1, _, _ = client_with_three_logged_in_users
    start, end = next_suitable_timeslot()

    _, proposal = create_proposal(
        client=client,
        access_token=token1,
        starts_at=start,
        ends_at=end,
        movie_title="Tenet",
        room="Room A",
    )
    proposal_id = proposal["id"]

    with freeze_time(start + timedelta(minutes=1)):
        token2 = fresh_token(client, VALID_USERNAME_2, VALID_PASSWORD_2)
        status_code, response = add_vote(client=client, proposal_id=proposal_id, access_token=token2)
        assert status_code == HTTPStatus.BAD_REQUEST
        assert response["detail"] == "Voting is not allowed for this proposal anymore."


def test_vote_for_missing_proposal_is_rejected(client_with_three_logged_in_users) -> None:
    client, _, token2, _ = client_with_three_logged_in_users

    status_code, response = add_vote(client=client, proposal_id=999999, access_token=token2)
    assert status_code == HTTPStatus.NOT_FOUND
    assert response["detail"] == "Proposal not found."


def test_vote_without_authentication_is_rejected(client_with_three_logged_in_users) -> None:
    client, _, _, _ = client_with_three_logged_in_users
    
    status_code, response = add_vote(client=client, proposal_id=1, access_token=None)
    assert status_code == HTTPStatus.UNAUTHORIZED
    assert response["detail"] == "Authentication required."
