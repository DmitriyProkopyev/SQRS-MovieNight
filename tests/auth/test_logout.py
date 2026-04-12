from datetime import timedelta
import uuid

from http import HTTPStatus

from movienight.core.jwt_decoder import decode_access_token
from movienight.core.clock import utcnow
from tests.auth.conftest import LOGOUT_ENDPOINT, VALID_USERNAME
from tests.auth.conftest import logout, forge_access_token, create_broken_access_token
from tests.conftest import WRONG_CONTENT_TYPES


def test_valid(client_with_logged_in_user) -> None:
    client, token = client_with_logged_in_user
    status_code, response = logout(client=client, access_token=token)
    assert status_code == HTTPStatus.OK

    assert "message" in response, f"Logging out did not return any message: {response}"
    assert response["message"] == f"User '{VALID_USERNAME}' was logged out."


def test_after_expiration(client_with_logged_in_user) -> None:
    client, original = client_with_logged_in_user
    subject = decode_access_token(original)["sub"]

    token = forge_access_token(subject=subject, issue_offset=-100, expiration_offset=-10)
    status_code, response = logout(client=client, access_token=token)
    assert status_code == HTTPStatus.UNAUTHORIZED

    assert "detail" in response, f"No error details were returned upon logging out using an expired token: {response}"
    assert response["detail"] == "Invalid token."

    token = forge_access_token(subject=subject, issue_offset=100, expiration_offset=1000)
    status_code, response = logout(client=client, access_token=token)
    assert status_code == HTTPStatus.UNAUTHORIZED

    assert "detail" in response, f"No error details were returned upon logging out using a future token: {response}"
    assert response["detail"] == "Invalid token."


def test_tampered_wrong_subject(client_with_logged_in_user) -> None:
    client, original = client_with_logged_in_user
    subject = decode_access_token(original)["sub"]
    token = forge_access_token(subject=str(int(subject) + 1), subject_tamper=subject, jti_tamper=None, issue_offset=-100, expiration_offset=100, break_signature=True)

    status_code, response = logout(client=client, access_token=token)
    assert status_code == HTTPStatus.UNAUTHORIZED
    assert "detail" in response, f"No error details were returned upon logging out using a forged token: {response}"
    assert response["detail"] == "Invalid token."


def test_tampered_wrong_jti(client_with_logged_in_user) -> None:
    client, original = client_with_logged_in_user
    subject = decode_access_token(original)["sub"]
    token = forge_access_token(subject=subject, subject_tamper=None, jti_tamper=str(uuid.uuid4()), issue_offset=-100, expiration_offset=100, break_signature=True)

    status_code, response = logout(client=client, access_token=token)
    assert status_code == HTTPStatus.UNAUTHORIZED
    assert "detail" in response, f"No error details were returned upon logging out using a forged token: {response}"
    assert response["detail"] == "Invalid token."


def test_malformed_token(client_with_logged_in_user) -> None:
    client, _ = client_with_logged_in_user

    token = create_broken_access_token(subject="1", jti=str(uuid.uuid4()), iat=str(utcnow()))
    status_code, _ = logout(client=client, access_token=token)
    assert status_code == HTTPStatus.UNAUTHORIZED

    token = create_broken_access_token(subject="1", jti=str(uuid.uuid4()), exp=str(utcnow() + timedelta(seconds=100)))
    status_code, _ = logout(client=client, access_token=token)
    assert status_code == HTTPStatus.UNAUTHORIZED

    token = create_broken_access_token(subject="1", iat=str(utcnow()), exp=str(utcnow() + timedelta(seconds=100)))
    status_code, _ = logout(client=client, access_token=token)
    assert status_code == HTTPStatus.UNAUTHORIZED

    token = create_broken_access_token(jti=str(uuid.uuid4()), iat=str(utcnow()), exp=str(utcnow() + timedelta(seconds=100)))
    status_code, _ = logout(client=client, access_token=token)
    assert status_code == HTTPStatus.UNAUTHORIZED

    token = create_broken_access_token(subject=str(uuid.uuid4()), jti=str(uuid.uuid4()), 
                                       iat=str(utcnow()), exp=str(utcnow() + timedelta(seconds=100)))
    status_code, _ = logout(client=client, access_token=token)
    assert status_code == HTTPStatus.UNAUTHORIZED

    token = create_broken_access_token(subject="1", jti="1", 
                                       iat=str(utcnow()), exp=str(utcnow() + timedelta(seconds=100)))
    status_code, _ = logout(client=client, access_token=token)
    assert status_code == HTTPStatus.UNAUTHORIZED

    token = create_broken_access_token(subject="1", jti=str(uuid.uuid4()), 
                                       iat="test", exp=str(utcnow() + timedelta(seconds=100)))
    status_code, _ = logout(client=client, access_token=token)
    assert status_code == HTTPStatus.UNAUTHORIZED

    token = create_broken_access_token(subject="1", jti=str(uuid.uuid4()), 
                                       iat=str(utcnow()), exp="test")
    status_code, _ = logout(client=client, access_token=token)
    assert status_code == HTTPStatus.UNAUTHORIZED


def test_many_with_same_token(client_with_logged_in_user) -> None:
    client, token = client_with_logged_in_user
    status_code, response = logout(client=client, access_token=token)
    assert status_code == HTTPStatus.OK

    for i in range(3):
        status_code, response = logout(client=client, access_token=token)
        assert status_code == HTTPStatus.UNAUTHORIZED

        assert "detail" in response, f"No error details were returned upon repeated logout: {response}"
        assert response["detail"] == "Token is no longer valid."


def test_malformed_request(client_with_logged_in_user) -> None:
    client, token = client_with_logged_in_user
    status_code, _ = logout(client=client, access_token=None)
    assert status_code == HTTPStatus.UNAUTHORIZED

    status_code, _ = logout(client=client, access_token=str(uuid.uuid4()))
    assert status_code == HTTPStatus.BAD_REQUEST

    response = client.post(LOGOUT_ENDPOINT, 
                          headers={"accept": "application/json", 
                                   "Content-Type": "application/json",
                                   "Authorization": f"Basic {token}"})
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_wrong_accept_types(client_with_logged_in_user):
    client, token = client_with_logged_in_user
    for accept_type in WRONG_CONTENT_TYPES:
        status_code, _ = logout(client=client, access_token=token, accept=accept_type)
        assert status_code == HTTPStatus.BAD_REQUEST


def test_wrong_content_types(client_with_logged_in_user) -> None:
    client, token = client_with_logged_in_user
    for content_type in WRONG_CONTENT_TYPES:
        status_code, _ = logout(client=client, access_token=token, content_type=content_type)
        assert status_code == HTTPStatus.BAD_REQUEST


def test_wrong_http_methods(client_with_logged_in_user) -> None:
    client, token = client_with_logged_in_user
    response = client.get(LOGOUT_ENDPOINT, 
                          headers={"accept": "application/json", 
                                   "Content-Type": "application/json",
                                   "Authorization": f"Bearer {token}"})
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    response = client.head(LOGOUT_ENDPOINT, 
                          headers={"accept": "application/json", 
                                   "Content-Type": "application/json",
                                   "Authorization": f"Bearer {token}"})
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    response = client.put(LOGOUT_ENDPOINT, 
                          headers={"accept": "application/json", 
                                   "Content-Type": "application/json",
                                   "Authorization": f"Bearer {token}"})
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    response = client.patch(LOGOUT_ENDPOINT, 
                          headers={"accept": "application/json", 
                                   "Content-Type": "application/json",
                                   "Authorization": f"Bearer {token}"})
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    response = client.delete(LOGOUT_ENDPOINT, 
                          headers={"accept": "application/json", 
                                   "Content-Type": "application/json",
                                   "Authorization": f"Bearer {token}"})
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
