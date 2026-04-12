import base64
import pytest
import json
import jwt

from datetime import timedelta
from fastapi.testclient import TestClient
from movienight.main import app
from movienight.db.base import Base
from movienight.core.clock import utcnow
from movienight.db.session import engine, settings
from typing import Dict
from uuid import uuid4


REGISTRATION_ENDPOINT = "/api/v1/auth/register"
LOGIN_ENDPOINT = "/api/v1/auth/login"
LOGOUT_ENDPOINT = "/api/v1/auth/logout"
ME_ENDPOINT = "/api/v1/auth/me"

VALID_USERNAME = "MyUniqueUsername"
VALID_PASSWORD = "H224!lse_I89C*&-mn"
VALID_USERNAME_2 = "Another_Valid_Username"
VALID_PASSWORD_2 = "o;89(Pgp9--nw)_v2b!f"

WRONG_CONTENT_TYPES = ["text/html", "text/plain", "text/css", "text/javascript", 
                          "application/xml", "application/pdf", "image/png", "image/jpeg",
                          "audio/mpeg", "video/mp4", "multipart/form-data"]


def _construct_headers(accept: str, content_type: str, access_token: str) -> Dict[str, str]:
    headers = { }
    if accept:
        headers["accept"] = accept
    if content_type:
        headers["Content-Type"] = content_type
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    return headers


def _construct_payload(username: str, password: str) -> Dict[str, str]:
    data = { }
    if username is not None:
        data["username"] = username
    if password is not None:
        data["password"] = password

    return data


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def register(client: TestClient, username: str, password: str, accept="application/json", content_type="application/json", access_token=None):
    headers = _construct_headers(accept=accept, content_type=content_type, access_token=access_token)
    payload = _construct_payload(username=username, password=password)
    response = client.post(REGISTRATION_ENDPOINT, json=payload, headers=headers)

    return response.status_code, response.json()


def login(client: TestClient, username: str, password: str, accept="application/json", content_type="application/json", access_token=None):
    headers = _construct_headers(accept=accept, content_type=content_type, access_token=access_token)
    payload = _construct_payload(username=username, password=password)
    response = client.post(LOGIN_ENDPOINT, json=payload, headers=headers)

    return response.status_code, response.json()


def logout(client: TestClient, access_token, accept="application/json", content_type="application/json"):
    headers = _construct_headers(accept=accept, content_type=content_type, access_token=access_token)
    response = client.post(LOGOUT_ENDPOINT, headers=headers)

    return response.status_code, response.json()


def me(client: TestClient, access_token, accept="application/json", content_type="application/json"):
    headers = _construct_headers(accept=accept, content_type=content_type, access_token=access_token)
    response = client.get(ME_ENDPOINT, headers=headers)

    return response.status_code, response.json()


def create_broken_access_token(subject: str = None, 
                               jti: str = None, 
                               iat: str = None, 
                               exp: str = None, 
                               custom: Dict[str, str] = None):
    payload = { }
    if subject:
        payload["sub"] = subject
    if jti:
        payload["jti"] = jti
    if iat:
        payload["iat"] = iat
    if exp:
        payload["exp"] = exp

    if custom:
        for key in custom:
            payload[key] = custom[key]

    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def forge_access_token(subject: str, subject_tamper: str = None, jti_tamper: str = None, issue_offset=0, expiration_offset=0, break_signature=False):
    payload = {
        "sub": subject,
        "jti": str(uuid4()),
        "iat": int(utcnow().timestamp() + issue_offset),
        "exp": int(utcnow().timestamp() + expiration_offset),
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    if not break_signature:
        return token

    header_b64, payload_b64, signature_b64 = token.split(".")
    tampered_payload = json.loads(_b64url_decode(payload_b64))
    
    if subject_tamper is not None:
        tampered_payload["sub"] = subject_tamper

    if jti_tamper is not None:
        tampered_payload["jti"] = jti_tamper

    tampered_payload_b64 = _b64url_encode(
        json.dumps(tampered_payload, separators=(",", ":")).encode()
    )

    return ".".join([header_b64, tampered_payload_b64, signature_b64])


@pytest.fixture(scope="function")
def default_client():
    with TestClient(app, base_url="http://127.0.0.1:8000") as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="module")
def client_with_users():
    with TestClient(app, base_url="http://127.0.0.1:8000") as test_client:
        register(client=test_client, username=VALID_USERNAME, password=VALID_PASSWORD)
        register(client=test_client, username=VALID_USERNAME_2, password=VALID_PASSWORD_2)
        yield test_client

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def client_with_logged_in_user():
    with TestClient(app, base_url="http://127.0.0.1:8000") as test_client:
        register(client=test_client, username=VALID_USERNAME, password=VALID_PASSWORD)
        register(client=test_client, username=VALID_USERNAME_2, password=VALID_PASSWORD_2)

        _, response = login(client=test_client, username=VALID_USERNAME, password=VALID_PASSWORD)
        yield test_client, response["access_token"]

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
