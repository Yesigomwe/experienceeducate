"""
Builder helper for constructing attendance payloads in tests.

Keeps test cases declarative — each test only overrides the field(s) it
cares about, rather than re-typing the full JSON structure every time.
"""
import copy

VALID_PARTICIPANT = {
    "participant_id": "YTH-8821",
    "status": "PRESENT",
}

VALID_PAYLOAD = {
    "mentor_id": "MNT-1042",
    "bootcamp_id": "KMP-2026-09",
    "session_date": "2026-09-11",
    "participants": [VALID_PARTICIPANT],
}


def valid_payload(**overrides):
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload.update(overrides)
    return payload


def with_participants(participants, **overrides):
    return valid_payload(participants=participants, **overrides)


def participant(**overrides):
    p = copy.deepcopy(VALID_PARTICIPANT)
    p.update(overrides)
    return p
