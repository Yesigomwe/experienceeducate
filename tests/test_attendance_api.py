"""
Automated test suite for POST /api/v1/attendance.

Run with: pytest tests/ -v
(see README.md for full setup instructions)
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.mock_api import app
from tests.helpers.api_client import AttendanceApiClient
from tests.helpers.payload_builder import valid_payload, with_participants, participant


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield AttendanceApiClient(test_client)


# ---------------------------------------------------------------------------
# 1. Happy path
# ---------------------------------------------------------------------------

def test_valid_payload_returns_201_and_success(client):
    response = client.submit(valid_payload())

    assert response.status_code == 201
    body = response.get_json()
    assert body["status"] == "success"
    assert body["participants_recorded"] == 1


# ---------------------------------------------------------------------------
# 2. Validation failures -> 400
# ---------------------------------------------------------------------------

def test_missing_mentor_id_returns_400(client):
    payload = valid_payload()
    del payload["mentor_id"]

    response = client.submit(payload)

    assert response.status_code == 400
    assert "mentor_id" in response.get_json()["error"]


def test_missing_bootcamp_id_returns_400(client):
    payload = valid_payload()
    del payload["bootcamp_id"]

    response = client.submit(payload)

    assert response.status_code == 400
    assert "bootcamp_id" in response.get_json()["error"]


@pytest.mark.parametrize("bad_age", [14, 25, -1, 100])
def test_age_out_of_bounds_returns_400(client, bad_age):
    # age isn't in the real payload schema, but the brief states it as it out as a validation example.
    # I will test it too assuming that it is supported as an optional field.
    payload = with_participants([participant(age=bad_age)])

    response = client.submit(payload)

    assert response.status_code == 400
    assert "age" in response.get_json()["error"]


def test_invalid_status_string_returns_400(client):
    payload = with_participants([participant(status="LATE")])

    response = client.submit(payload)

    assert response.status_code == 400
    assert "status" in response.get_json()["error"]


# ---------------------------------------------------------------------------
# 3. Edge cases
# ---------------------------------------------------------------------------

def test_empty_participants_array_returns_400(client):
    payload = with_participants([])

    response = client.submit(payload)

    assert response.status_code == 400
    assert "participants" in response.get_json()["error"]


def test_duplicate_participant_ids_in_same_request_returns_400(client):
    dup_id = "P999999"
    payload = with_participants([
        participant(participant_id=dup_id, full_name="Youth A"),
        participant(participant_id=dup_id, full_name="Youth B"),
    ])

    response = client.submit(payload)

    assert response.status_code == 400
    assert "duplicate" in response.get_json()["error"]


def test_multiple_valid_participants_in_one_request_returns_201(client):
    payload = with_participants([
        participant(participant_id="P000001", full_name="Youth A"),
        participant(participant_id="P000002", full_name="Youth B", age=24),
    ])

    response = client.submit(payload)

    assert response.status_code == 201
    assert response.get_json()["participants_recorded"] == 2
