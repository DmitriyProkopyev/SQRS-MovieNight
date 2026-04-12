import uuid

from http import HTTPStatus

from movienight.core.clock import utcnow
from movienight.core.security import decode_access_token
from tests.auth.conftest import ME_ENDPOINT, VALID_USERNAME, WRONG_CONTENT_TYPES
from tests.auth.conftest import logout, me, forge_access_token, create_broken_access_token


def test_valid(client_with_logged_in_user) -> None:
    client, token = client_with_logged_in_user
    status_code, response = me(client=client, access_token=token)
    assert status_code == HTTPStatus.OK

    assert "id" in response, f"Checking out the current user did not return any id: {response}"
    assert "username" in response, f"Checking out the current user did not return any username: {response}"
    assert response["username"] == VALID_USERNAME


def test_expired_token(client_with_logged_in_user) -> None:
    client, original = client_with_logged_in_user
    subject = decode_access_token(original)["sub"]

    token = forge_access_token(subject=subject, issue_offset=-100, expiration_offset=-10)
    status_code, response = me(client=client, access_token=token)
    assert status_code == HTTPStatus.UNAUTHORIZED

    assert "detail" in response, f"No error details were returned upon checking out the current user using an expired token: {response}"
    assert response["detail"] == "Invalid token."

    token = forge_access_token(subject=subject, issue_offset=100, expiration_offset=1000)
    status_code, response = me(client=client, access_token=token)
    assert status_code == HTTPStatus.UNAUTHORIZED

    assert "detail" in response, f"No error details were returned upon checking out the current user using a future token {response}"
    assert response["detail"] == "Invalid token."


def test_tampered_wrong_subject(client_with_logged_in_user) -> None:
    client, original = client_with_logged_in_user
    subject = decode_access_token(original)["sub"]
    token = forge_access_token(subject=str(int(subject) + 1), subject_tamper=subject, jti_tamper=None, issue_offset=-100, expiration_offset=100, break_signature=True)

    status_code, response = me(client=client, access_token=token)
    assert status_code == HTTPStatus.UNAUTHORIZED
    assert "detail" in response, f"No error details were returned upon chceking out the current user using a forged token: {response}"
    assert response["detail"] == "Invalid token."


def test_tampered_wrong_jti(client_with_logged_in_user) -> None:
    client, original = client_with_logged_in_user
    subject = decode_access_token(original)["sub"]
    token = forge_access_token(subject=subject, subject_tamper=None, jti_tamper=str(uuid.uuid4()), issue_offset=-100, expiration_offset=100, break_signature=True)

    status_code, response = me(client=client, access_token=token)
    assert status_code == HTTPStatus.UNAUTHORIZED
    assert "detail" in response, f"No error details were returned upon checking out the current user using a forged token: {response}"
    assert response["detail"] == "Invalid token."


def test_malformed_token(client_with_logged_in_user) -> None:
    client, _ = client_with_logged_in_user

    token = create_broken_access_token(subject="1", jti=str(uuid.uuid4()), iat=str(utcnow()))
    status_code, _ = me(client=client, access_token=token)
    assert status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    token = create_broken_access_token(subject="1", jti=str(uuid.uuid4()), exp=str(utcnow() + 100))
    status_code, _ = me(client=client, access_token=token)
    assert status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    token = create_broken_access_token(subject="1", iat=str(utcnow()), exp=str(utcnow() + 100))
    status_code, _ = me(client=client, access_token=token)
    assert status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    token = create_broken_access_token(jti=str(uuid.uuid4()), iat=str(utcnow()), exp=str(utcnow() + 100))
    status_code, _ = me(client=client, access_token=token)
    assert status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    token = create_broken_access_token(subject=str(uuid.uuid4()), jti=str(uuid.uuid4()), 
                                       iat=str(utcnow()), exp=str(utcnow() + 100))
    status_code, _ = me(client=client, access_token=token)
    assert status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    token = create_broken_access_token(subject="1", jti="1", 
                                       iat=str(utcnow()), exp=str(utcnow() + 100))
    status_code, _ = me(client=client, access_token=token)
    assert status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    token = create_broken_access_token(subject="1", jti=str(uuid.uuid4()), 
                                       iat="test", exp=str(utcnow() + 100))
    status_code, _ = me(client=client, access_token=token)
    assert status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    token = create_broken_access_token(subject="1", jti=str(uuid.uuid4()), 
                                       iat=str(utcnow()), exp="test")
    status_code, _ = me(client=client, access_token=token)
    assert status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_same_token_after_logout(client_with_logged_in_user) -> None:
    client, token = client_with_logged_in_user
    status_code, response = logout(client=client, access_token=token)
    assert status_code == HTTPStatus.OK

    status_code, response = me(client=client, access_token=token)
    assert status_code == HTTPStatus.UNAUTHORIZED

    assert "detail" in response, f"No error details were returned upon checking out the current user after logout: {response}"
    assert response["detail"] == "Token is no longer valid."


def test_malformed_request(client_with_logged_in_user) -> None:
    client, token = client_with_logged_in_user
    status_code, _ = me(client=client, access_token=None)
    assert status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    status_code, _ = me(client=client, access_token=str(uuid.uuid4()))
    assert status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    response = client.get(ME_ENDPOINT, 
                          headers={"accept": "application/json", 
                                   "Content-Type": "application/json",
                                   "Authorization": f"Basic {token}"})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_wrong_accept_types(client_with_logged_in_user):
    client, token = client_with_logged_in_user
    for accept_type in WRONG_CONTENT_TYPES:
        status_code, _ = me(client=client, access_token=token, accept=accept_type)
        assert status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_wrong_content_types(client_with_logged_in_user) -> None:
    client, token = client_with_logged_in_user
    for content_type in WRONG_CONTENT_TYPES:
        status_code, _ = me(client=client, access_token=token, content_type=content_type)
        assert status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_wrong_http_methods(client_with_logged_in_user) -> None:
    client, token = client_with_logged_in_user
    response = client.post(ME_ENDPOINT, 
                          headers={"accept": "application/json", 
                                   "Content-Type": "application/json",
                                   "Authorization": f"Bearer {token}"})
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    response = client.head(ME_ENDPOINT, 
                          headers={"accept": "application/json", 
                                   "Content-Type": "application/json",
                                   "Authorization": f"Bearer {token}"})
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    response = client.put(ME_ENDPOINT, 
                          headers={"accept": "application/json", 
                                   "Content-Type": "application/json",
                                   "Authorization": f"Bearer {token}"})
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    response = client.patch(ME_ENDPOINT, 
                          headers={"accept": "application/json", 
                                   "Content-Type": "application/json",
                                   "Authorization": f"Bearer {token}"})
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    response = client.delete(ME_ENDPOINT, 
                          headers={"accept": "application/json", 
                                   "Content-Type": "application/json",
                                   "Authorization": f"Bearer {token}"})
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
