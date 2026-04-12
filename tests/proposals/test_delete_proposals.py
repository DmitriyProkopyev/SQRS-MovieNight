from datetime import datetime, timedelta
from freezegun import freeze_time
from http import HTTPStatus

from tests.proposals.conftest import delete_proposal, find_proposals
from tests.conftest import WRONG_CONTENT_TYPES


def test_valid(client_with_proposals_and_users):
    client, token, _ = client_with_proposals_and_users
    ids = list(find_proposals(client, token))
    assert len(ids) == 4, f"Number of pre-determined proposals does not match the expectation: {ids}"

    id_to_delete = ids[0]
    status_code, response = delete_proposal(client, access_token=token, id=id_to_delete)
    assert status_code == HTTPStatus.OK
    
    assert "message" in response, f"Deleting a proposal did not return a message: {response}"
    assert response["message"] == "Proposal deleted."

    ids = list(find_proposals(client, token))
    assert len(ids) == 3
    assert id_to_delete not in ids


def test_delete_proposal_of_another_user(client_with_proposals_and_users):
    client, token1, token2 = client_with_proposals_and_users
    ids = sorted(list(find_proposals(client, token1)))
    id_to_delete1 = ids[0]
    id_to_delete2 = ids[2]

    status_code, response = delete_proposal(client, access_token=token1, id=id_to_delete2)
    assert status_code == HTTPStatus.FORBIDDEN
    
    assert "detail" in response, f"Deleting another user's proposal returned no error details: {response}"
    assert response["detail"] == "You can delete only your own proposals."

    status_code, response = delete_proposal(client, access_token=token2, id=id_to_delete1)
    assert status_code == HTTPStatus.FORBIDDEN
    
    assert "detail" in response, f"Deleting another user's proposal returned no error details: {response}"
    assert response["detail"] == "You can delete only your own proposals."


def test_delete_non_existent_proposal(client_with_proposals_and_users):
    client, token, _ = client_with_proposals_and_users

    status_code, response = delete_proposal(client, access_token=token, id=999)
    assert status_code == HTTPStatus.NOT_FOUND
    
    assert "detail" in response, f"Deleting non-existent proposal returned no error details: {response}"
    assert response["detail"] == "Proposal not found."


def test_delete_past_proposal(client_with_proposals_and_users):
    client, token, _ = client_with_proposals_and_users
    hours_later = datetime.now() + timedelta(hours=20)
    id_to_delete = next(find_proposals(client, access_token=token))

    with freeze_time(hours_later):
        status_code, response = delete_proposal(client, access_token=token, id=id_to_delete)
        assert status_code == HTTPStatus.BAD_REQUEST

        assert "detail" in response, f"Deleting past proposal returned no error details: {response}"
        assert response["detail"] == "Past proposals cannot be deleted."


def test_not_authenticated(client_with_proposals_and_users) -> None:
    client, token, _ = client_with_proposals_and_users
    id_to_delete = next(find_proposals(client, access_token=token))

    status_code, response = delete_proposal(client, access_token=None, id=id_to_delete)
    assert status_code == HTTPStatus.UNAUTHORIZED

    assert "detail" in response, f"No error details were returned upon trying to delete a proposal while not authenticated: {response}"
    assert response["detail"] == "Authentication required."


def test_malformed_requests(client_with_proposals_and_users) -> None:
    client, token, _ = client_with_proposals_and_users

    status_code, _ = delete_proposal(client, access_token=token, id=None)
    assert status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_wrong_accept_types(client_with_proposals_and_users):
    client, token, _ = client_with_proposals_and_users

    for accept_type in WRONG_CONTENT_TYPES:
        status_code, _ = delete_proposal(client, access_token=token, id=1, accept=accept_type)
        assert status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_wrong_content_types(client_with_proposals_and_users) -> None:
    client, token, _ = client_with_proposals_and_users

    for accept_type in WRONG_CONTENT_TYPES:
        status_code, _ = delete_proposal(client, access_token=token, id=1, accept=accept_type)
        assert status_code == HTTPStatus.UNPROCESSABLE_ENTITY
