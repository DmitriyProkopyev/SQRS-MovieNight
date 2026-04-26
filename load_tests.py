from __future__ import annotations

import random
import threading
from datetime import UTC, datetime, time, timedelta

import requests
from locust import HttpUser, between, task


API_PREFIX = "/api/v1"
LOAD_TEST_PASSWORD = "LocustPass_123!"
LOAD_TEST_TITLES = (
    "Locust Load Test A",
    "Locust Load Test B",
)


def next_two_hour_slot_start() -> datetime:
    now = datetime.now(UTC) + timedelta(days=1)
    slot_hour = ((now.hour // 2) * 2 + 2) % 24
    slot_date = now.date()
    if slot_hour == 0:
        slot_date = slot_date + timedelta(days=1)

    return datetime.combine(
        slot_date,
        time(hour=slot_hour, tzinfo=UTC),
    )


class MovieNightUser(HttpUser):
    wait_time = between(1, 3)

    _setup_lock = threading.Lock()
    _shared_proposal_ids: list[int] = []

    def on_start(self) -> None:
        self.username = f"locust_user_{random.randint(1000, 999999)}"
        self.password = LOAD_TEST_PASSWORD
        self.base_headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        self.auth_headers = dict(self.base_headers)
        self.active_vote_proposal_id: int | None = None

        token = self.authenticate_user(
            username=self.username,
            password=self.password,
        )
        self.auth_headers["Authorization"] = f"Bearer {token}"
        self.ensure_shared_proposals()

    def api_url(self, path: str) -> str:
        return f"{self.host.rstrip('/')}{path}"

    def authenticate_user(
        self,
        username: str,
        password: str,
    ) -> str:
        payload = {
            "username": username,
            "password": password,
        }

        login_response = requests.post(
            self.api_url(f"{API_PREFIX}/auth/login"),
            json=payload,
            headers=self.base_headers,
            timeout=15,
        )
        if login_response.status_code == 200:
            return login_response.json()["access_token"]

        register_response = requests.post(
            self.api_url(f"{API_PREFIX}/auth/register"),
            json=payload,
            headers=self.base_headers,
            timeout=15,
        )
        if register_response.status_code == 201:
            return register_response.json()["access_token"]

        raise RuntimeError(
            "Unable to authenticate load-test user "
            f"{username}: login={login_response.status_code}, "
            f"register={register_response.status_code}"
        )

    def ensure_shared_proposals(self) -> None:
        if self.__class__._shared_proposal_ids:
            return

        with self.__class__._setup_lock:
            if self.__class__._shared_proposal_ids:
                return

            owner_tokens = [
                self.authenticate_user("locust_owner_a", LOAD_TEST_PASSWORD),
                self.authenticate_user("locust_owner_b", LOAD_TEST_PASSWORD),
            ]

            proposal_ids = self.find_shared_proposals(owner_tokens[0])
            if len(proposal_ids) < len(LOAD_TEST_TITLES):
                start_at = next_two_hour_slot_start()
                owners = [
                    ("Room C", LOAD_TEST_TITLES[0], owner_tokens[0]),
                    ("Room C", LOAD_TEST_TITLES[1], owner_tokens[1]),
                ]

                for room, movie_title, token in owners:
                    self.create_shared_proposal(
                        room=room,
                        movie_title=movie_title,
                        start_at=start_at,
                        token=token,
                    )

                proposal_ids = self.find_shared_proposals(owner_tokens[0])

            if len(proposal_ids) < len(LOAD_TEST_TITLES):
                raise RuntimeError(
                    "Shared proposals for Locust voting were not prepared."
                )

            self.__class__._shared_proposal_ids = proposal_ids

    def create_shared_proposal(
        self,
        room: str,
        movie_title: str,
        start_at: datetime,
        token: str,
    ) -> None:
        payload = {
            "room": room,
            "movie_title": movie_title,
            "starts_at": start_at.isoformat().replace("+00:00", "Z"),
            "ends_at": (
                start_at + timedelta(hours=2)
            ).isoformat().replace("+00:00", "Z"),
        }
        headers = dict(self.base_headers)
        headers["Authorization"] = f"Bearer {token}"

        response = requests.post(
            self.api_url(f"{API_PREFIX}/proposals"),
            json=payload,
            headers=headers,
            timeout=15,
        )
        if response.status_code in (200, 201, 400):
            return

        raise RuntimeError(
            "Unable to create shared proposal "
            f"{movie_title}: {response.status_code} {response.text}"
        )

    def find_shared_proposals(self, token: str) -> list[int]:
        headers = dict(self.base_headers)
        headers["Authorization"] = f"Bearer {token}"

        response = requests.get(
            self.api_url(f"{API_PREFIX}/catalog"),
            headers=headers,
            timeout=15,
        )
        response.raise_for_status()
        payload = response.json()

        proposal_ids: list[int] = []
        for group in payload.get("groups", []):
            for proposal in group.get("proposals", []):
                if proposal.get("movie_title") in LOAD_TEST_TITLES:
                    proposal_ids.append(proposal["id"])

        return sorted(set(proposal_ids))

    @task(3)
    def view_schedule(self) -> None:
        with self.client.get(
            f"{API_PREFIX}/schedule",
            headers=self.auth_headers,
            name="GET /api/v1/schedule",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Unexpected schedule status: {response.status_code}"
                )

    @task(2)
    def view_catalog(self) -> None:
        with self.client.get(
            f"{API_PREFIX}/catalog",
            headers=self.auth_headers,
            name="GET /api/v1/catalog",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Unexpected catalog status: {response.status_code}"
                )

    @task(2)
    def toggle_vote(self) -> None:
        if not self.__class__._shared_proposal_ids:
            return

        if self.active_vote_proposal_id is None:
            proposal_id = random.choice(self.__class__._shared_proposal_ids)
            with self.client.post(
                f"{API_PREFIX}/proposals/{proposal_id}/votes",
                headers=self.auth_headers,
                name="POST /api/v1/proposals/{proposal_id}/votes",
                catch_response=True,
            ) as response:
                if response.status_code == 201:
                    self.active_vote_proposal_id = proposal_id
                    response.success()
                elif response.status_code in (400, 404):
                    response.failure(
                        f"Vote request returned {response.status_code}: "
                        f"{response.text}"
                    )
                else:
                    response.failure(
                        f"Unexpected vote status: {response.status_code}"
                    )
            return

        with self.client.delete(
            f"{API_PREFIX}/proposals/{self.active_vote_proposal_id}/votes",
            headers=self.auth_headers,
            name="DELETE /api/v1/proposals/{proposal_id}/votes",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                self.active_vote_proposal_id = None
                response.success()
            elif response.status_code in (400, 404):
                self.active_vote_proposal_id = None
                response.failure(
                    f"Unvote request returned {response.status_code}: "
                    f"{response.text}"
                )
            else:
                response.failure(
                    f"Unexpected unvote status: {response.status_code}"
                )
