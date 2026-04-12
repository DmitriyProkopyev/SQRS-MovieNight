import pytest

from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from movienight.main import app
from movienight.db.base import Base
from movienight.db.session import engine

from tests.auth.conftest import register, login, _construct_headers
from tests.auth.conftest import VALID_USERNAME, VALID_PASSWORD, VALID_USERNAME_2, VALID_PASSWORD_2


PROPOSAL_ENDPOINT = "/api/v1/proposals"


def next_suitable_timeslot(after: datetime = None) -> datetime:
    if not after:
        after = datetime.now()

    if after.hour % 2 == 0:
        start = after + timedelta(hours=2)
    else:
        start = after + timedelta(hours=3)

    start = start.replace(minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=2)
    return start, end


def create_proposal(client: TestClient,
                    access_token: str,
                    starts_at: datetime,
                    ends_at: datetime,
                    movie_title: str,
                    room: str,
                    accept: str = "application/json",
                    content_type: str = "application/json"):
    headers = _construct_headers(accept=accept, content_type=content_type, access_token=access_token)

    payload = { }
    if starts_at:
        payload["starts_at"] = str(starts_at)
    if ends_at:
        payload["ends_at"] = str(ends_at)
    if movie_title:
        payload["movie_title"] = movie_title
    if room:
        payload["room"] = room

    response = client.post(PROPOSAL_ENDPOINT, json=payload, headers=headers)
    return response.status_code, response.json()


def delete_proposal(client: TestClient,
                    access_token: str,
                    id: int,
                    accept: str = "application/json",
                    content_type: str = "application/json"):
    headers = _construct_headers(accept=accept, content_type=content_type, access_token=access_token)
    response = client.delete(f"{PROPOSAL_ENDPOINT}/{id}", headers=headers)
    return response.status_code, response.json()


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
