from datetime import datetime, timedelta
from freezegun import freeze_time
from http import HTTPStatus

from movienight.core.jwt_decoder import decode_access_token
from tests.proposals.conftest import create_proposal, next_suitable_timeslot, PROPOSAL_ENDPOINT
from tests.conftest import ESOTERIC_STRINGS, WRONG_CONTENT_TYPES


VALID_MOVIE_TITLE = "Interstellar"
VALID_ROOM = "Room A"
VALID_MOVIE_TITLE_2 = "Interstellar 2"
VALID_ROOM_2 = "Room B"
VALID_MOVIE_TITLE_3 = "Interstellar 3"
VALID_MOVIE_TITLE_4 = "Interstellar 4"
VALID_MOVIE_TITLE_5 = "Interstellar 5"
VALID_MOVIE_TITLE_6 = "Interstellar 6"


def test_unique_valid(client_with_logged_in_users) -> None:
    client, token1, token2 = client_with_logged_in_users
    start, end = next_suitable_timeslot()
    status_code, response = create_proposal(client,
                                            access_token=token1,
                                            starts_at=start,
                                            ends_at=end,
                                            movie_title=VALID_MOVIE_TITLE,
                                            room=VALID_ROOM)
    assert status_code == HTTPStatus.CREATED

    assert "id" in response, f"Creating a proposal did not return an id: {response}"
    assert response["room"] == VALID_ROOM, f"Creating a proposal returned a wrong room: {response['room']}"
    assert response["movie_title"] == VALID_MOVIE_TITLE, f"Creating a proposal returned a wrong movie title: {response['movie_title']}"
    assert response["starts_at"] == str(start).replace(' ', 'T'), f"Creating a proposal returned a wrong start time: {response['starts_at']}"
    assert response["ends_at"] == str(end).replace(' ', 'T'), f"Creating a proposal returned a wrong end time: {response['ends_at']}"

    creator_id = decode_access_token(token1)["sub"]
    assert int(response["creator_id"]) == int(creator_id), f"Creating a proposal returned a wrong creator id: {response['creator_id']}"

    start2, end2 = next_suitable_timeslot(start - timedelta(seconds=1))
    status_code, response2 = create_proposal(client,
                                             access_token=token2,
                                             starts_at=start2,
                                             ends_at=end2,
                                             movie_title=VALID_MOVIE_TITLE_2,
                                             room=VALID_ROOM_2)
    assert status_code == HTTPStatus.CREATED

    assert response["id"] != response2["id"], f"Creating two distinct proposals returned identical ids: {response['id']}"
    assert response["creator_id"] != response2["creator_id"], f"Creating proposals by distinct authors returned identical creator ids: {response['creator_id']}"


def test_room_overlap_only(client_with_logged_in_users) -> None:
    client, token, _ = client_with_logged_in_users
    start, end = next_suitable_timeslot()
    status_code, _ = create_proposal(client,
                                     access_token=token,
                                     starts_at=start,
                                     ends_at=end,
                                     movie_title=VALID_MOVIE_TITLE,
                                     room=VALID_ROOM)
    assert status_code == HTTPStatus.CREATED

    start2, end2 = next_suitable_timeslot(start - timedelta(seconds=1))
    status_code, _ = create_proposal(client,
                                     access_token=token,
                                     starts_at=start2,
                                     ends_at=end2,
                                     movie_title=VALID_MOVIE_TITLE_2,
                                     room=VALID_ROOM)
    assert status_code == HTTPStatus.CREATED


def test_time_overlap_only(client_with_logged_in_users) -> None:
    client, token, _ = client_with_logged_in_users
    start, end = next_suitable_timeslot()
    status_code, _ = create_proposal(client,
                                     access_token=token,
                                     starts_at=start,
                                     ends_at=end,
                                     movie_title=VALID_MOVIE_TITLE,
                                     room=VALID_ROOM)
    assert status_code == HTTPStatus.CREATED

    status_code, _ = create_proposal(client,
                                     access_token=token,
                                     starts_at=start,
                                     ends_at=end,
                                     movie_title=VALID_MOVIE_TITLE_2,
                                     room=VALID_ROOM_2)
    assert status_code == HTTPStatus.CREATED


def test_create_in_past(client_with_logged_in_users) -> None:
    client, token, _ = client_with_logged_in_users
    start, end = next_suitable_timeslot(datetime.now() - timedelta(hours=6))
    status_code, response = create_proposal(client,
                                     access_token=token,
                                     starts_at=start,
                                     ends_at=end,
                                     movie_title=VALID_MOVIE_TITLE,
                                     room=VALID_ROOM)
    assert status_code == HTTPStatus.BAD_REQUEST
    assert "detail" in response, f"No error details were returned upon creating a proposal in the past: {response}"
    assert response["detail"] == "Proposal start time cannot be in the past."


def test_ends_before_starts(client_with_logged_in_users) -> None:
    client, token, _ = client_with_logged_in_users
    end, start = next_suitable_timeslot()
    status_code, response = create_proposal(client,
                                     access_token=token,
                                     starts_at=start,
                                     ends_at=end,
                                     movie_title=VALID_MOVIE_TITLE,
                                     room=VALID_ROOM)
    assert status_code == HTTPStatus.BAD_REQUEST
    assert "detail" in response, f"No error details were returned upon creating a proposal that ends before it starts: {response}"
    assert response["detail"] == "Proposal end time must be later than start time."


def test_wrong_timeslot_bounds(client_with_logged_in_users) -> None:
    client, token, _ = client_with_logged_in_users
    now = datetime.now() + timedelta(hours=4)
    start = now.replace(minute=42, second=42, microsecond=42)
    end = start + timedelta(hours=2)

    status_code, response = create_proposal(client,
                                     access_token=token,
                                     starts_at=start,
                                     ends_at=end,
                                     movie_title=VALID_MOVIE_TITLE,
                                     room=VALID_ROOM)
    assert status_code == HTTPStatus.BAD_REQUEST
    assert "detail" in response, f"No error details were returned upon creating a proposal at an invalid timeslot: {response}"
    assert response["detail"] == "Proposal start time must match a 2-hour slot: 00:00, 02:00, 04:00, and so on."


def test_wrong_timeslot_duration(client_with_logged_in_users) -> None:
    client, token, _ = client_with_logged_in_users
    start, _ = next_suitable_timeslot()
    end = start
    status_code, response = create_proposal(client,
                                     access_token=token,
                                     starts_at=start,
                                     ends_at=end,
                                     movie_title=VALID_MOVIE_TITLE,
                                     room=VALID_ROOM)
    assert status_code == HTTPStatus.BAD_REQUEST
    assert "detail" in response, f"No error details were returned upon creating a proposal with an invalid duration: {response}"
    assert response["detail"] == "Proposal end time must be later than start time."

    end += timedelta(hours=4)
    status_code, response = create_proposal(client,
                                     access_token=token,
                                     starts_at=start,
                                     ends_at=end,
                                     movie_title=VALID_MOVIE_TITLE,
                                     room=VALID_ROOM)
    assert status_code == HTTPStatus.BAD_REQUEST
    assert "detail" in response, f"No error details were returned upon creating a proposal of invalid duration: {response}"
    assert response["detail"] == "Proposal must last exactly 2 hours."

    end = start + timedelta(hours=1)
    status_code, response = create_proposal(client,
                                     access_token=token,
                                     starts_at=start,
                                     ends_at=end,
                                     movie_title=VALID_MOVIE_TITLE,
                                     room=VALID_ROOM)
    assert status_code == HTTPStatus.BAD_REQUEST
    assert "detail" in response, f"No error details were returned upon creating a proposal of invalid duration: {response}"
    assert response["detail"] == "Proposal must last exactly 2 hours."


def test_duplicate_proposals(client_with_logged_in_users) -> None:
    client, token1, token2 = client_with_logged_in_users
    start, end = next_suitable_timeslot()
    status_code, _ = create_proposal(client,
                                            access_token=token1,
                                            starts_at=start,
                                            ends_at=end,
                                            movie_title=VALID_MOVIE_TITLE,
                                            room=VALID_ROOM)
    assert status_code == HTTPStatus.CREATED

    status_code, response = create_proposal(client,
                                            access_token=token1,
                                            starts_at=start,
                                            ends_at=end,
                                            movie_title=VALID_MOVIE_TITLE,
                                            room=VALID_ROOM)
    assert status_code == HTTPStatus.BAD_REQUEST
    assert "detail" in response, f"No error details were returned upon creating duplicate proposals: {response}"
    assert response["detail"] == "An overlapping proposal for the same room and movie already exists."

    status_code, response = create_proposal(client,
                                            access_token=token2,
                                            starts_at=start,
                                            ends_at=end,
                                            movie_title=VALID_MOVIE_TITLE,
                                            room=VALID_ROOM)
    assert status_code == HTTPStatus.BAD_REQUEST
    assert "detail" in response, f"No error details were returned upon creating duplicate proposals: {response}"
    assert response["detail"] == "An overlapping proposal for the same room and movie already exists."


def test_overlap_too_many_proposals(client_with_logged_in_users) -> None:
    client, token1, token2 = client_with_logged_in_users
    start, end = next_suitable_timeslot()

    use_first = True
    for movie_title in [VALID_MOVIE_TITLE, VALID_MOVIE_TITLE_2, 
                        VALID_MOVIE_TITLE_3, VALID_MOVIE_TITLE_4, VALID_MOVIE_TITLE_5]:
        token = token1 if use_first else token2
        use_first = not use_first
        status_code, _ = create_proposal(client,
                                         access_token=token,
                                         starts_at=start,
                                         ends_at=end,
                                         movie_title=movie_title,
                                         room=VALID_ROOM)
        assert status_code == HTTPStatus.CREATED

    status_code, response = create_proposal(client,
                                            access_token=token2,
                                            starts_at=start,
                                            ends_at=end,
                                            movie_title=VALID_MOVIE_TITLE_6,
                                            room=VALID_ROOM)
    assert status_code == HTTPStatus.BAD_REQUEST
    assert "detail" in response, f"No error details were returned upon creating more than 5 overlapping proposals: {response}"
    assert response["detail"] == "Too many overlapping proposals already exist in this room."


# @freeze_time("2026-04-12 13:50:10")
# def test_starts_too_soon(client_with_logged_in_users) -> None:
#     client, token, _ = client_with_logged_in_users
#     start, end = next_suitable_timeslot(datetime.now() - timedelta(hours=1))

#     status_code, response = create_proposal(client,
#                                             access_token=token,
#                                             starts_at=start,
#                                             ends_at=end,
#                                             movie_title=VALID_MOVIE_TITLE,
#                                             room=VALID_ROOM)
#     assert status_code == HTTPStatus.BAD_REQUEST
#     assert "detail" in response, f"No error details were returned upon creating a proposal starting in less than an hour: {response}"
#     assert response["detail"] == "New proposals should start later than an hour away."


def test_not_authenticated(client_with_logged_in_users) -> None:
    client, _, _ = client_with_logged_in_users
    start, end = next_suitable_timeslot()

    status_code, response = create_proposal(client,
                                            access_token=None,
                                            starts_at=start,
                                            ends_at=end,
                                            movie_title=VALID_MOVIE_TITLE,
                                            room=VALID_ROOM)
    assert status_code == HTTPStatus.UNAUTHORIZED
    assert "detail" in response, f"No error details were returned upon creating an unathorized proposal: {response}"
    assert response["detail"] == "Authentication required."


def test_non_existent_rooms(client_with_logged_in_users) -> None:
    client, token, _ = client_with_logged_in_users
    start, end = next_suitable_timeslot()

    status_code, response = create_proposal(client,
                                            access_token=token,
                                            starts_at=start,
                                            ends_at=end,
                                            movie_title=VALID_MOVIE_TITLE,
                                            room="Non-existent room")
    assert status_code == HTTPStatus.BAD_REQUEST
    assert "detail" in response, f"No error details were returned upon creating a proposal in a non-existent room: {response}"
    assert response["detail"] == "Proposals can only be created in already existing rooms."


def test_whitespaces_in_movie_titles(client_with_logged_in_users) -> None:
    client, token, _ = client_with_logged_in_users
    leading = "    " + VALID_MOVIE_TITLE
    trailing = VALID_MOVIE_TITLE_2 + "     "

    start, end = next_suitable_timeslot()
    status_code, response = create_proposal(client,
                                            access_token=token,
                                            starts_at=start,
                                            ends_at=end,
                                            movie_title=leading,
                                            room=VALID_ROOM)
    assert status_code == HTTPStatus.CREATED
    assert response["movie_title"] == VALID_MOVIE_TITLE

    status_code, response = create_proposal(client,
                                            access_token=token,
                                            starts_at=start,
                                            ends_at=end,
                                            movie_title=trailing,
                                            room=VALID_ROOM)
    assert status_code == HTTPStatus.CREATED
    assert response["movie_title"] == VALID_MOVIE_TITLE_2


def test_too_long_movie_titles(client_with_logged_in_users) -> None:
    client, token, _ = client_with_logged_in_users

    borderline_valid_title = 'A' * 255
    too_long_title_1 = 'A' * 256
    too_long_title_2 = 'A' * 300
    too_long_title_3 = 'A' * 400
    
    start, end = next_suitable_timeslot()
    for title in [too_long_title_1, too_long_title_2, too_long_title_3]:
        status_code, response = create_proposal(client,
                                            access_token=token,
                                            starts_at=start,
                                            ends_at=end,
                                            movie_title=title,
                                            room=VALID_ROOM)
        assert status_code == HTTPStatus.BAD_REQUEST
        assert "detail" in response, f"No error details were returned upon creating a proposal with a too long movie title: {response}"
        assert response["detail"] == "Movie title length cannot exceed 255 characters."

    status_code, response = create_proposal(client,
                                            access_token=token,
                                            starts_at=start,
                                            ends_at=end,
                                            movie_title=borderline_valid_title,
                                            room=VALID_ROOM)
    assert status_code == HTTPStatus.CREATED


def test_esoteric_movie_titles(client_with_logged_in_users) -> None:
    client, token, _ = client_with_logged_in_users
    start, end = next_suitable_timeslot()

    for title in ESOTERIC_STRINGS:
        status_code, response = create_proposal(client,
                                            access_token=token,
                                            starts_at=start,
                                            ends_at=end,
                                            movie_title=title,
                                            room=VALID_ROOM)
        assert status_code == HTTPStatus.BAD_REQUEST
        assert "detail" in response, f"No error details were returned upon creating a proposal with esoteric characters: {response}"
        assert response["detail"] == "Movie title cannot contain esoteric non-printable characters."


def test_malformed_requests(client_with_logged_in_users) -> None:
    client, token, _ = client_with_logged_in_users
    start, end = next_suitable_timeslot()

    status_code, _ = create_proposal(client=client,
                                     access_token=None,
                                     starts_at=start,
                                     ends_at=end,
                                     movie_title=VALID_MOVIE_TITLE,
                                     room=VALID_ROOM)
    assert status_code == HTTPStatus.UNAUTHORIZED

    status_code, _ = create_proposal(client=client,
                                     access_token=token,
                                     starts_at=None,
                                     ends_at=end,
                                     movie_title=VALID_MOVIE_TITLE,
                                     room=VALID_ROOM)
    assert status_code == HTTPStatus.BAD_REQUEST

    status_code, _ = create_proposal(client=client,
                                     access_token=token,
                                     starts_at=start,
                                     ends_at=None,
                                     movie_title=VALID_MOVIE_TITLE,
                                     room=VALID_ROOM)
    assert status_code == HTTPStatus.BAD_REQUEST

    status_code, _ = create_proposal(client=client,
                                     access_token=token,
                                     starts_at=start,
                                     ends_at=end,
                                     movie_title=None,
                                     room=VALID_ROOM)
    assert status_code == HTTPStatus.BAD_REQUEST

    status_code, _ = create_proposal(client=client,
                                     access_token=token,
                                     starts_at=start,
                                     ends_at=end,
                                     movie_title=VALID_MOVIE_TITLE,
                                     room=None)
    assert status_code == HTTPStatus.BAD_REQUEST

    status_code, _ = create_proposal(client=client,
                                     access_token=token,
                                     starts_at="starts_at",
                                     ends_at=end,
                                     movie_title=VALID_MOVIE_TITLE,
                                     room=VALID_ROOM)
    assert status_code == HTTPStatus.BAD_REQUEST

    status_code, _ = create_proposal(client=client,
                                     access_token=token,
                                     starts_at=start,
                                     ends_at="ends_at",
                                     movie_title=VALID_MOVIE_TITLE,
                                     room=VALID_ROOM)
    assert status_code == HTTPStatus.BAD_REQUEST


def test_wrong_accept_types(client_with_logged_in_users):
    client, token, _ = client_with_logged_in_users
    start, end = next_suitable_timeslot()

    for accept_type in WRONG_CONTENT_TYPES:
        status_code, _ = create_proposal(client=client,
                                         access_token=token,
                                         starts_at=start,
                                         ends_at=end,
                                         movie_title=VALID_MOVIE_TITLE,
                                         room=VALID_ROOM,
                                         accept=accept_type)
        assert status_code == HTTPStatus.BAD_REQUEST


def test_wrong_content_types(client_with_logged_in_users) -> None:
    client, token, _ = client_with_logged_in_users
    start, end = next_suitable_timeslot()

    for content_type in WRONG_CONTENT_TYPES:
        status_code, _ = create_proposal(client=client,
                                         access_token=token,
                                         starts_at=start,
                                         ends_at=end,
                                         movie_title=VALID_MOVIE_TITLE,
                                         room=VALID_ROOM,
                                         content_type=content_type)
        assert status_code == HTTPStatus.BAD_REQUEST


def test_wrong_http_methods(client_with_logged_in_users) -> None:
    client, token, _ = client_with_logged_in_users
    start, end = next_suitable_timeslot()
    
    response = client.get(PROPOSAL_ENDPOINT, 
                          headers={"accept": "application/json", 
                                   "Content-Type": "application/json",
                                   "Authorization": f"Bearer {token}"})
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    response = client.head(PROPOSAL_ENDPOINT, 
                          headers={"accept": "application/json", 
                                   "Content-Type": "application/json",
                                   "Authorization": f"Bearer {token}"})
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    response = client.put(PROPOSAL_ENDPOINT, 
                          json={"starts_at": str(start),
                                "ends_at": str(end),
                                "movie_title": VALID_MOVIE_TITLE,
                                "room": VALID_ROOM}, 
                          headers={"accept": "application/json", 
                                   "Content-Type": "application/json",
                                   "Authorization": f"Bearer {token}"})
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    response = client.patch(PROPOSAL_ENDPOINT, 
                          json={"starts_at": str(start),
                                "ends_at": str(end),
                                "movie_title": VALID_MOVIE_TITLE,
                                "room": VALID_ROOM}, 
                          headers={"accept": "application/json", 
                                   "Content-Type": "application/json",
                                   "Authorization": f"Bearer {token}"})
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
