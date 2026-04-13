import pytest

from fastapi.testclient import TestClient

from movienight.db.base import Base
from movienight.db.session import engine
from movienight.main import app

from tests.auth.conftest import VALID_USERNAME, VALID_USERNAME_2, VALID_USERNAME_3
from tests.auth.conftest import VALID_PASSWORD, VALID_PASSWORD_2, VALID_PASSWORD_3
from tests.auth.conftest import register, login
from tests.conftest import construct_headers


VOTE_ENDPOINT_TEMPLATE = "/api/v1/proposals/{proposal_id}/votes"


def add_vote(client: TestClient, proposal_id: int, access_token: str | None,
             accept="application/json", content_type="application/json"):
    headers = construct_headers(accept=accept, content_type=content_type, access_token=access_token)

    if access_token is not None:
        headers["Authorization"] = f"Bearer {access_token}"

    response = client.post(VOTE_ENDPOINT_TEMPLATE.format(proposal_id=proposal_id), headers=headers)
    return response.status_code, response.json()


def remove_vote(client: TestClient, proposal_id: int, access_token: str | None,
                accept="application/json", content_type="application/json"):
    headers = construct_headers(accept=accept, content_type=content_type, access_token=access_token)
    response = client.delete(VOTE_ENDPOINT_TEMPLATE.format(proposal_id=proposal_id), headers=headers)
    return response.status_code, response.json()


def fresh_token(client: TestClient, username: str, password: str) -> str:
    _, response = login(client=client, username=username, password=password)
    return response["access_token"]


@pytest.fixture(scope="function")
def client_with_three_logged_in_users():
    with TestClient(app, base_url="http://127.0.0.1:8000") as test_client:
        _, token1 = register(client=test_client, username=VALID_USERNAME, password=VALID_PASSWORD)
        _, token2 = register(client=test_client, username=VALID_USERNAME_2, password=VALID_PASSWORD_2)
        _, token3 = register(client=test_client, username=VALID_USERNAME_3, password=VALID_PASSWORD_3)

        token1 = fresh_token(client=test_client, username=VALID_USERNAME, password=VALID_PASSWORD)
        token2 = fresh_token(client=test_client, username=VALID_USERNAME_2, password=VALID_PASSWORD_2)
        token3 = fresh_token(client=test_client, username=VALID_USERNAME_3, password=VALID_PASSWORD_3)

        yield test_client, token1, token2, token3

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
