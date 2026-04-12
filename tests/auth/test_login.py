import time
import jwt

from fastapi.testclient import TestClient
from http import HTTPStatus

from movienight.core.security import decode_access_token
from tests.auth.conftest import login, LOGIN_ENDPOINT, VALID_USERNAME, VALID_PASSWORD, VALID_USERNAME_2, VALID_PASSWORD_2, WRONG_CONTENT_TYPES


def test_valid(client_with_users: TestClient) -> None:
    status_code, response = login(client_with_users, username=VALID_USERNAME, password=VALID_PASSWORD)
    assert status_code == HTTPStatus.OK

    assert "access_token" in response, f"Login returned no access token: {response}"
    assert "token_type" in response, f"Login returned no token type: {response}"
    assert "user" in response, f"Login returned no user data: {response}"
    assert "id" in response["user"], f"Login returned no id in user data: {response['user']}"
    assert "username" in response["user"], f"Login returned no username in user data: {response['user']}"

    assert response["token_type"] == "bearer", f"Login returned wrong token type: {response['token_type']}"
    assert response["user"]["username"] == VALID_USERNAME

    status_code, response2 = login(client_with_users, username=VALID_USERNAME_2, password=VALID_PASSWORD_2)
    assert status_code == HTTPStatus.OK

    assert response["access_token"] != response2["access_token"]

    header = jwt.get_unverified_header(response["access_token"])
    assert header["alg"] == "HS256", f"Unexpected algorithm in a JWT token: {header['alg']}"
    assert header["typ"] == "JWT", f"Unexpected token type: {header['type']}"
    
    payload1 = decode_access_token(response["access_token"])
    payload2 = decode_access_token(response2["access_token"])
    assert int(payload1["sub"]) == int(response["user"]["id"]), f"JWT token payload refers to the wrong user: {payload1['sub']}"
    assert payload1["jti"] != payload2["jti"], f"Logging into different accounts returns identical token ids: {payload1['jti']}"

    now = time.time()
    issued_at = int(payload1["iat"])
    assert issued_at <= now, f"JWT token issue time is not in the past: {issued_at} > {now}"

    expires_at = int(payload1["exp"])
    assert now < expires_at, f"JWT token issued at login has already expired: {expires_at} <= {now}"


def test_invalid_username(client_with_users: TestClient) -> None:
    status_code, response = login(client_with_users, username=VALID_USERNAME+"1", password=VALID_PASSWORD)
    assert status_code == HTTPStatus.UNAUTHORIZED

    assert "detail" in response, f"Login with an invalid username returned no error detail: {response}"
    assert response["detail"] == "Invalid username or password."


def test_username_case_sensitivity(client_with_users: TestClient) -> None:
    status_code, response = login(client_with_users, username=VALID_USERNAME.lower(), password=VALID_PASSWORD)
    assert status_code == HTTPStatus.UNAUTHORIZED

    assert "detail" in response, f"Login with an invalid username returned no error detail: {response}"
    assert response["detail"] == "Invalid username or password."

    status_code, response = login(client_with_users, username=VALID_USERNAME.upper(), password=VALID_PASSWORD)
    assert status_code == HTTPStatus.UNAUTHORIZED

    assert "detail" in response, f"Login with an invalid username returned no error detail: {response}"
    assert response["detail"] == "Invalid username or password."


def test_invalid_password(client_with_users: TestClient) -> None:
    status_code, response = login(client_with_users, username=VALID_USERNAME, password=VALID_PASSWORD+"1")
    assert status_code == HTTPStatus.UNAUTHORIZED

    assert "detail" in response, f"Login with an invalid password returned no error detail: {response}"
    assert response["detail"] == "Invalid username or password."


def test_password_case_sensitivity(client_with_users: TestClient) -> None:
    status_code, response = login(client_with_users, username=VALID_USERNAME, password=VALID_PASSWORD.lower())
    assert status_code == HTTPStatus.UNAUTHORIZED

    assert "detail" in response, f"Login with an invalid password returned no error detail: {response}"
    assert response["detail"] == "Invalid username or password."

    status_code, response = login(client_with_users, username=VALID_USERNAME, password=VALID_PASSWORD.upper())
    assert status_code == HTTPStatus.UNAUTHORIZED

    assert "detail" in response, f"Login with an invalid password returned no error detail: {response}"
    assert response["detail"] == "Invalid username or password."


def test_while_logged_in_as_the_same_user(client_with_users: TestClient) -> None:
    status_code, response = login(client_with_users, username=VALID_USERNAME, password=VALID_PASSWORD)
    assert status_code == HTTPStatus.OK

    access_token = response["access_token"]
    status_code, response = login(client_with_users, username=VALID_USERNAME, password=VALID_PASSWORD, access_token=access_token)
    assert status_code == HTTPStatus.BAD_REQUEST

    assert "detail" in response, f"Login while already logged in as the same user returned no error detail: {response}"
    assert response["detail"] == "User is already authenticated."


def test_while_logged_in_as_a_different_user(client_with_users: TestClient) -> None:
    status_code, response = login(client_with_users, username=VALID_USERNAME, password=VALID_PASSWORD)
    assert status_code == HTTPStatus.OK

    access_token = response["access_token"]
    status_code, response = login(client_with_users, username=VALID_USERNAME_2, password=VALID_PASSWORD_2, access_token=access_token)
    assert status_code == HTTPStatus.BAD_REQUEST

    assert "detail" in response, f"Login while already logged in as the same user returned no error detail: {response}"
    assert response["detail"] == "User is already authenticated."


def test_malformed_request(client_with_users: TestClient) -> None:
    status_code, _ = login(client=client_with_users, username=None, password=VALID_PASSWORD)
    assert status_code == HTTPStatus.BAD_REQUEST

    status_code, _ = login(client=client_with_users, username=VALID_USERNAME, password=None)
    assert status_code == HTTPStatus.BAD_REQUEST

    status_code, _ = login(client=client_with_users, username=None, password=None)
    assert status_code == HTTPStatus.BAD_REQUEST


def test_wrong_accept_types(client_with_users: TestClient):
    for accept_type in WRONG_CONTENT_TYPES:
        status_code, _ = login(client=client_with_users, username=VALID_USERNAME, password=VALID_PASSWORD, accept=accept_type)
        assert status_code == HTTPStatus.BAD_REQUEST


def test_wrong_content_types(client_with_users: TestClient) -> None:
    for content_type in WRONG_CONTENT_TYPES:
        status_code, _ = login(client=client_with_users, username=VALID_USERNAME, password=VALID_PASSWORD, content_type=content_type)
        assert status_code == HTTPStatus.BAD_REQUEST


def test_wrong_http_methods(client_with_users: TestClient) -> None:
    response = client_with_users.get(LOGIN_ENDPOINT, 
                          headers={"accept": "application/json", "Content-Type": "application/json"})
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    response = client_with_users.head(LOGIN_ENDPOINT, 
                          headers={"accept": "application/json", "Content-Type": "application/json"})
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    response = client_with_users.put(LOGIN_ENDPOINT, 
                          json={"username": VALID_USERNAME, "password": VALID_PASSWORD}, 
                          headers={"accept": "application/json", "Content-Type": "application/json"})
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    response = client_with_users.patch(LOGIN_ENDPOINT, 
                          json={"username": VALID_USERNAME, "password": VALID_PASSWORD}, 
                          headers={"accept": "application/json", "Content-Type": "application/json"})
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    response = client_with_users.delete(LOGIN_ENDPOINT, 
                          headers={"accept": "application/json", "Content-Type": "application/json"})
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
