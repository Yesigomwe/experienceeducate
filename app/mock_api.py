"""
Mock implementation of POST /api/v1/attendance.

This stands in for the real engineering-team endpoint so the test suite
in tests/test_attendance_api.py has something concrete to run against.

Schema is based on the actual sample payload from the brief:
    {
      "mentor_id": "MNT-1042",
      "bootcamp_id": "KMP-2026-09",
      "session_date": "2026-09-11",
      "participants": [
        {"participant_id": "YTH-8821", "status": "PRESENT"},
        {"participant_id": "YTH-8822", "status": "ABSENT"}
      ]
    }

Note: the sample payload does NOT include full_name or age per participant
(those belong to the *registration* endpoint, not attendance check-in) — but
the brief's task list still calls out "age out of bounds" as an example
validation case. To satisfy both without contradicting the real schema, age
is treated as an OPTIONAL field: if a client includes it, it's validated
(15-24); if omitted, that's fine. See README.md "Assumptions" for more.
"""
from flask import Flask, request, jsonify

app = Flask(__name__)

ALLOWED_STATUSES = {"PRESENT", "ABSENT"}
MIN_AGE, MAX_AGE = 15, 24

# In-memory "database" so we can demonstrate the duplicate-participant edge case.
_saved_attendance_records = []


def _validate_participant(p, seen_ids):
    """Returns an error string, or None if the participant record is valid."""
    if "participant_id" not in p or not p["participant_id"]:
        return "participant_id is required"
    if p["participant_id"] in seen_ids:
        return f"duplicate participant_id '{p['participant_id']}' in request"
    seen_ids.add(p["participant_id"])

    if p.get("status") not in ALLOWED_STATUSES:
        return f"status must be one of {sorted(ALLOWED_STATUSES)}"

    # age is optional at the attendance endpoint (see module docstring) —
    # only validated if the client happens to include it.
    if "age" in p:
        try:
            age = int(p["age"])
        except (TypeError, ValueError):
            return "age must be an integer"
        if not (MIN_AGE <= age <= MAX_AGE):
            return f"age must be between {MIN_AGE} and {MAX_AGE}"

    return None


@app.route("/api/v1/attendance", methods=["POST"])
def record_attendance():
    payload = request.get_json(silent=True)

    if payload is None:
        return jsonify({"error": "request body must be valid JSON"}), 400

    if "mentor_id" not in payload or not str(payload["mentor_id"]).strip():
        return jsonify({"error": "mentor_id is required"}), 400

    if "bootcamp_id" not in payload or not str(payload["bootcamp_id"]).strip():
        return jsonify({"error": "bootcamp_id is required"}), 400

    participants = payload.get("participants")
    if not isinstance(participants, list) or len(participants) == 0:
        return jsonify({"error": "participants must be a non-empty array"}), 400

    seen_ids = set()
    for participant in participants:
        error = _validate_participant(participant, seen_ids)
        if error:
            return jsonify({"error": error}), 400

    _saved_attendance_records.append(payload)
    return jsonify({
        "status": "success",
        "mentor_id": payload["mentor_id"],
        "participants_recorded": len(participants),
    }), 201


if __name__ == "__main__":
    app.run(debug=True)
