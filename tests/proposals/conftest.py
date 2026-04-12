import pytest

from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from typing import Iterable

from movienight.main import app
from movienight.db.base import Base
from movienight.db.session import engine

from tests.auth.conftest import register, login, _construct_headers
from tests.auth.conftest import VALID_USERNAME, VALID_PASSWORD, VALID_USERNAME_2, VALID_PASSWORD_2


PROPOSAL_ENDPOINT = "/api/v1/proposals"
HOME_ENDPOINT = "/api/v1/home"

VALID_MOVIE_TITLE = "Interstellar"
VALID_ROOM = "Room A"
VALID_MOVIE_TITLE_2 = "Interstellar 2"
VALID_ROOM_2 = "Room B"
VALID_MOVIE_TITLE_3 = "Interstellar 3"
VALID_MOVIE_TITLE_4 = "Interstellar 4"
VALID_MOVIE_TITLE_5 = "Interstellar 5"
VALID_MOVIE_TITLE_6 = "Interstellar 6"


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


def create_proposal(
    client,
    access_token,
    starts_at,
    ends_at,
    movie_title,
    room,
    accept="application/json",
    content_type="application/json",
):
    headers = {
        "accept": accept,
        "Content-Type": content_type,
    }

    if access_token is not None:
        headers["Authorization"] = f"Bearer {access_token}"

    payload = {
        "starts_at": str(starts_at),
        "ends_at": str(ends_at),
        "movie_title": movie_title,
        "room": room,
    }

    if content_type == "application/json":
        response = client.post(
            PROPOSAL_ENDPOINT,
            json=payload,
            headers=headers,
        )
    else:
        response = client.post(
            PROPOSAL_ENDPOINT,
            data=b"not-json",
            headers=headers,
        )

    try:
        body = response.json()
    except Exception:
        body = {}

    return response.status_code, body

def delete_proposal(client: TestClient,
                    access_token: str,
                    id: int,
                    accept: str = "application/json",
                    content_type: str = "application/json"):
    headers = _construct_headers(accept=accept, content_type=content_type, access_token=access_token)
    response = client.delete(f"{PROPOSAL_ENDPOINT}/{id}", headers=headers)
    return response.status_code, response.json()


def find_proposals(client: TestClient, access_token: str) -> Iterable[int]:
    headers = _construct_headers(accept="application/json", content_type="application/json", access_token=access_token)
    response = client.get(HOME_ENDPOINT, headers=headers).json()

    for group in response["groups"]:
        for proposal in group["proposals"]:
            yield int(proposal["id"])


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


@pytest.fixture(scope="function")
def client_with_proposals_and_users():
    with TestClient(app, base_url="http://127.0.0.1:8000") as test_client:
        _, response = register(client=test_client, username=VALID_USERNAME, password=VALID_PASSWORD)
        _, response2 = register(client=test_client, username=VALID_USERNAME_2, password=VALID_PASSWORD_2)

        start, end = next_suitable_timeslot(datetime.now() + timedelta(hours=4))

        create_proposal(client=test_client,
                        access_token=response["access_token"],
                        starts_at=start,
                        ends_at=end,
                        movie_title=VALID_MOVIE_TITLE,
                        room=VALID_ROOM)
        create_proposal(client=test_client,
                        access_token=response["access_token"],
                        starts_at=start,
                        ends_at=end,
                        movie_title=VALID_MOVIE_TITLE_2,
                        room=VALID_ROOM_2)
        create_proposal(client=test_client,
                        access_token=response2["access_token"],
                        starts_at=start,
                        ends_at=end,
                        movie_title=VALID_MOVIE_TITLE_3,
                        room=VALID_ROOM)
        create_proposal(client=test_client,
                        access_token=response2["access_token"],
                        starts_at=start,
                        ends_at=end,
                        movie_title=VALID_MOVIE_TITLE_4,
                        room=VALID_ROOM_2)
        
        yield test_client, response["access_token"], response2["access_token"]

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
