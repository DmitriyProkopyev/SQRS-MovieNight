import random
import string

from fastapi.testclient import TestClient
from http import HTTPStatus

from tests.auth.conftest import register, REGISTRATION_ENDPOINT
from tests.auth.conftest import VALID_USERNAME, VALID_PASSWORD, VALID_USERNAME_2, VALID_PASSWORD_2
from tests.conftest import ESOTERIC_STRINGS, WRONG_CONTENT_TYPES


def test_valid(default_client: TestClient) -> None:
    status_code, response = register(client=default_client, username=VALID_USERNAME, password=VALID_PASSWORD)
    assert status_code == HTTPStatus.CREATED, f"Registration failed: {response}"

    assert "access_token" in response, f"Registration did not return access token: {response}"
    assert "token_type" in response, f"Registration did not return token type: {response}"
    assert response["token_type"] == "bearer", f"Registration token is not of type bearer: {response['token_type']}"

    assert "user" in response, f"Registration did not return the user data: {response}"
    assert "id" in response["user"], f"Registration did not return the user id: {response['user']}"
    assert "username" in response["user"], f"Registration did not return the username: {response['user']}"
    assert response["user"]["username"] == VALID_USERNAME, f"Registration returned wrong username: {response['user']['username']}"
    
    status_code2, response2 = register(client=default_client, username=VALID_USERNAME_2, password=VALID_PASSWORD_2)
    assert status_code2 == HTTPStatus.CREATED, f"Registration failed: {response}"

    assert response["access_token"] != response2["access_token"], f"Two registrations returned identical access tokens: {response['access_token']}"
    assert response["user"]["id"] != response2["user"]["id"] + 1, f"Two registrations returned identical user ids: {response['user']['id']}"
    assert response["user"]["username"] != response2["user"]["username"]


def test_duplicate_usernames(default_client: TestClient) -> None:
    status_code, response = register(client=default_client, username=VALID_USERNAME+"1", password=VALID_PASSWORD)
    assert status_code == HTTPStatus.CREATED, f"Registration failed: {response}"

    status_code, response = register(client=default_client, username=VALID_USERNAME+"1", password=VALID_PASSWORD_2)
    assert status_code == HTTPStatus.BAD_REQUEST, f"Repeated username registration did not return 400 BadRequest: {response}"

    assert "detail" in response, f"No error details were returned upon duplicate registration: {response}"
    assert response["detail"] == "Username is already taken."


def test_while_logged_in(default_client: TestClient) -> None:
    status_code, response = register(client=default_client, username=VALID_USERNAME, password=VALID_PASSWORD)
    assert status_code == HTTPStatus.CREATED, f"Registration failed: {response}"

    access_token = response["access_token"]
    status_code, response = register(client=default_client, username=VALID_USERNAME_2, password=VALID_PASSWORD_2, access_token=access_token)
    assert status_code == HTTPStatus.BAD_REQUEST, f"New account registration while logged in was not prevented: {response}"

    assert "detail" in response, f"No error details were returned upon logged in registration: {response}"
    assert response["detail"] == "Log out before creating a new account."


def test_whitespaces_in_usernames(default_client: TestClient) -> None:
    leading = "   surely_NoRmAL_usErnAMe_FOr-rEaL"
    trailing = "soMe_other_totAlLY-NorMAl_usErnaMe     "

    status_code, response = register(client=default_client, username=leading, password=VALID_PASSWORD)
    assert status_code == HTTPStatus.CREATED, f"Registration of a username with leading whitespaces failed: {response}"
    assert response["user"]["username"] == leading.strip()

    status_code, response = register(client=default_client, username=trailing, password=VALID_PASSWORD_2)
    assert status_code == HTTPStatus.CREATED, f"Registration of a username with trailing whitespaces failed: {response}"
    assert response["user"]["username"] == trailing.strip()


def test_special_characters_in_usernames(default_client: TestClient) -> None:
    random.seed(42)

    for forbidden_char in string.punctuation:
        if forbidden_char in {"_", "-"}:
            continue

        random_char = VALID_USERNAME[
            random.randint(0, len(VALID_USERNAME) - 1)
        ]
        username = VALID_USERNAME.replace(random_char, forbidden_char)

        status_code, response = register(
            client=default_client,
            username=username,
            password=VALID_PASSWORD,
        )
        assert status_code == HTTPStatus.BAD_REQUEST
        assert "detail" in response
        assert response["detail"] == (
            "Punctuation characters are not allowed in the username."
        )


def test_too_short_usernames(default_client: TestClient) -> None:
    empty_username = ""
    one_character_username = "a"
    two_character_username = "ab"
    three_character_username = "abc"

    for username in [empty_username, one_character_username, two_character_username]:
        status_code, response = register(client=default_client, username=username, password=VALID_PASSWORD)
        assert status_code == HTTPStatus.BAD_REQUEST
        assert "detail" in response, f"No error details were returned upon registration of a too short username: {response}"
        assert response["detail"] == "Username should contain at least three characters."

    status_code, response = register(client=default_client, username=three_character_username, password=VALID_PASSWORD)
    assert status_code == HTTPStatus.CREATED


def test_too_long_usernames(default_client: TestClient) -> None:
    borderline_valid_username = 'A' * 49
    too_long_username1 = 'A' * 50
    too_long_username2 = 'B' * 70
    too_long_username3 = 'C' * 100

    for username in [too_long_username1, too_long_username2, too_long_username3]:
        status_code, response = register(client=default_client, username=username, password=VALID_PASSWORD)
        assert status_code == HTTPStatus.BAD_REQUEST
        assert "detail" in response, f"No error details were returned upon registration of a too long username: {response}"
        assert response["detail"] == "Username length cannot exceed 100 characters."

    status_code, response = register(client=default_client, username=borderline_valid_username, password=VALID_PASSWORD)
    assert status_code == HTTPStatus.CREATED


def test_esoteric_usernames(default_client: TestClient) -> None:
    cc_cstring = "user\x00"                         # NUL (Cc)
    cf_left_to_right = "Hey my name is \u200E"      # LEFT‑TO‑RIGHT MARK (Cf)
    cf_right_to_left = "Hey I am the ad\u200Fmin"   # RIGHT‑TO‑LEFT MARK (Cf)
    cf_zero_width = "your friend\u200B"             # ZERO‑WIDTH SPACE (Cf)

    co_private = "verifi\xE0\x80\x80ed"             # U+E000 (Co) in UTF‑8 bytes
    cs_low = "mode\u2060rator"                      # U+D800 (Cs) surrogate in UTF‑8
    co_str = chr(0xE000) + "admin"                  # Private‑use char (Co)
    cs_str = "admin\u2060"                          # Low‑surrogate (Cs)

    for username in [cc_cstring, cf_left_to_right, cf_right_to_left, cf_zero_width, co_private, cs_low, co_str, cs_str]:
        status_code, response = register(client=default_client, username=username, password=VALID_PASSWORD)
        assert status_code == HTTPStatus.BAD_REQUEST
        assert "detail" in response, f"No error details were returned upon registration of an esoteric username: {response}"
        assert response["detail"] == "Username cannot contain esoteric or invisible characters."


def test_too_short_passwords(default_client: TestClient) -> None:
    five_characters = "T3St!"
    six_characters = "T3St1!"
    seven_characters = "@T3St1!"
    eight_characters = "@T3St1!_"

    for password in [five_characters, six_characters, seven_characters]:
        status_code, response = register(client=default_client, username=VALID_USERNAME, password=password)
        assert status_code == HTTPStatus.BAD_REQUEST
        assert "detail" in response, f"No error details were returned upon registration with a too short password: {response}"
        assert response["detail"] == "Password must contain at least 8 characters."

    status_code, response = register(client=default_client, username=VALID_USERNAME, password=eight_characters)
    assert status_code == HTTPStatus.CREATED


def test_too_long_passwords(default_client: TestClient) -> None:
    borderline_valid_password = ('A' * 252) + "a!1"
    too_long_password1 = 'A' * 253 + "a!1"
    too_long_password2 = 'B' * 300 + "a!1"
    too_long_password3 = 'C' * 400 + "a!1"

    for password in [too_long_password1, too_long_password2, too_long_password3]:
        status_code, response = register(client=default_client, username=VALID_USERNAME, password=password)
        assert status_code == HTTPStatus.BAD_REQUEST
        assert "detail" in response, f"No error details were returned upon registration with a too long password: {response}"
        assert response["detail"] == "Password length cannot exceed 255 characters."

    status_code, response = register(client=default_client, username=VALID_USERNAME, password=borderline_valid_password)
    assert status_code == HTTPStatus.CREATED


def test_weak_passwords(default_client: TestClient) -> None:
    only_lowercase = "longbutweaktestpasswordstring"
    only_uppercase = "LONGBUTWEAKTESTPASSWORDSTRING"
    only_digits = "129380249572098750934"
    only_special_characters = "@#$%^&*!()[]<>№;:}{"
    full_set_of_characters = "aR4m_(=)!31+-249<(#$v9B23V)"

    for password in [only_lowercase, only_uppercase, only_digits, only_special_characters]:
        status_code, response = register(client=default_client, username=VALID_USERNAME, password=password)
        assert status_code == HTTPStatus.BAD_REQUEST
        assert "detail" in response, f"No error details were returned upon registration with a simple password: {response}"
        assert response["detail"] == "Password must contain at least one lowercase letter, an uppercase letter, a digit, and a special character."

    status_code, response = register(client=default_client, username=VALID_USERNAME, password=full_set_of_characters)
    assert status_code == HTTPStatus.CREATED


def test_personal_info_in_passwords(default_client: TestClient) -> None:
    includes_username = VALID_PASSWORD + VALID_USERNAME + VALID_PASSWORD_2
    status_code, response = register(client=default_client, username=VALID_USERNAME, password=includes_username)
    assert status_code == HTTPStatus.BAD_REQUEST

    assert "detail" in response, f"No error details were returned upon registration with a password containing personal info: {response}"
    assert response["detail"] == "Password cannot contain public personal information, such as username."


def test_malformed_requests(default_client: TestClient) -> None:
    status_code, _ = register(client=default_client, username=None, password=VALID_PASSWORD)
    assert status_code == HTTPStatus.BAD_REQUEST

    status_code, _ = register(client=default_client, username=VALID_USERNAME, password=None)
    assert status_code == HTTPStatus.BAD_REQUEST

    status_code, _ = register(client=default_client, username=None, password=None)
    assert status_code == HTTPStatus.BAD_REQUEST


def test_wrong_accept_types(default_client: TestClient):
    for accept_type in WRONG_CONTENT_TYPES:
        status_code, _ = register(client=default_client, username=VALID_USERNAME, password=VALID_PASSWORD, accept=accept_type)
        assert status_code == HTTPStatus.BAD_REQUEST


def test_wrong_content_types(default_client: TestClient) -> None:
    for content_type in WRONG_CONTENT_TYPES:
        status_code, _ = register(client=default_client, username=VALID_USERNAME, password=VALID_PASSWORD, content_type=content_type)
        assert status_code == HTTPStatus.BAD_REQUEST


def test_wrong_http_methods(default_client: TestClient) -> None:
    response = default_client.get(REGISTRATION_ENDPOINT, 
                          headers={"accept": "application/json", "Content-Type": "application/json"})
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    response = default_client.head(REGISTRATION_ENDPOINT, 
                          headers={"accept": "application/json", "Content-Type": "application/json"})
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    response = default_client.put(REGISTRATION_ENDPOINT, 
                          json={"username": VALID_USERNAME, "password": VALID_PASSWORD}, 
                          headers={"accept": "application/json", "Content-Type": "application/json"})
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    response = default_client.patch(REGISTRATION_ENDPOINT, 
                          json={"username": VALID_USERNAME, "password": VALID_PASSWORD}, 
                          headers={"accept": "application/json", "Content-Type": "application/json"})
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    response = default_client.delete(REGISTRATION_ENDPOINT, 
                          headers={"accept": "application/json", "Content-Type": "application/json"})
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
