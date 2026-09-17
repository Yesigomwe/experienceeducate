# Educate! Senior QA Engineer — Practical Exercise

## Structure

- `docs/part1_qa_strategy.md` — Definition of Done, risk analysis, bug triage (Part 1)
- `app/mock_api.py` — Mock implementation of `POST /api/v1/attendance` used as the system under test
- `tests/test_attendance_api.py` — Automated test suite (Part 2)
- `tests/helpers/` — API client wrapper + payload builder helpers (keeps tests modular/readable)
- `docs/part3_framework_analysis.md` — Playwright vs. Cypress trade-off analysis (Part 3)
- `.github/workflows/test.yml` — CI/CD pipeline, runs on every PR to `main` and acts as a quality gate

## Running the tests locally

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

All test cases should pass. Covers:
- Happy path (valid payload → 201)
- Validation failures → 400 (missing `mentor_id`, age out of bounds, invalid `status`)
- Edge cases → 400 (empty `participants` array, duplicate `participant_id` in one request)
- A multi-participant happy path

## Assumptions made

The mock endpoint (`app/mock_api.py`) is built to match the actual sample payload given in the brief:

```json
{
  "mentor_id": "MNT-1042",
  "bootcamp_id": "KMP-2026-09",
  "session_date": "2026-09-11",
  "participants": [
    {"participant_id": "YTH-8821", "status": "PRESENT"},
    {"participant_id": "YTH-8822", "status": "ABSENT"}
  ]
}
```

A couple of things I had to reconcile and would confirm with the backend team in a real handoff:

- **`status` allowed values:** the sample only confirms `PRESENT`/`ABSENT` as valid and `"LATE"` as invalid.
- **`age` isn't in the sample payload**, but the task list still names "age out of bounds" as an example validation failure.I assume age and name belong to the another endpoint eg *registration* endpoint (captured once when a youth joins), not the *attendance* check-in endpoint (which just marks present/absent per session) — re-sending age on every attendance record would be redundant and a data-integrity risk if it ever drifted from the registration record. So I implemented `age` as an **optional** field on the attendance endpoint: validated if present, but not required — this satisfies the explicit test-case requirement without contradicting the real schema. I would also communicate this assumption to the Product owner.  
- **`participant_id` must be unique within a single request** — not explicitly stated, but implied by the "duplicate participant_ids" edge case in the task list.

## What I'd add with more time

- Tests against offline queue/sync behavior (Bug B scenario) — would need a real or emulated client with connectivity toggling, likely a separate integration-test layer rather than pure API tests.
- Contract tests against the real API schema once available (e.g. via a shared OpenAPI spec) instead of my own inferred mock.
- A Playwright E2E test covering the web registration form end-to-end, per the Part 3 recommendation.
- Load/performance check for the SMS confirmation service level agreement (Bug C).
