# Part 1: QA Strategy & Release Readiness

## 1. Definition of "Done" — Participant Registration & Attendance Feature

Before this feature ships to production, all of the following must be true:

- [ ] All three acceptance criteria (phone number,full name,age and district validation, offline queue + auto-sync, USSD SMS confirmation with 6-digit ID) must pass manual verification on both web and USSD paths.
- [ ] Age boundary is enforced server-side (not just client-side); 15 and 24 accepted, 14 and 25 rejected.
- [ ] Automated regression suite is green in CI, including happy path, validation failures, and edge cases.
- [ ] Offline queue behavior is verified on a real low-connectivity device or with network throttle on a simulator ,including app kill and restart while records are still queued.
- [ ] No duplicate participant records are created when a registration is retried after a dropped connection (scenario for Bug B).
- [ ] SMS confirmation delivery time is measured against an agreed timeframe (e.g. under 30 seconds) across both MTN and Airtel, not just one.
- [ ] Participant IDs are verified unique across the full existing dataset, not just within a single test batch.
- [ ] Error states have user-facing messages in  the languages understandable to the the field mentors, not raw error codes like 500.
- [ ] Rollback plan exists and has been tested (e.g. feature flag to disable USSD flow without taking down web registration).
- [ ] Product Owner has signed off against the acceptance criteria in a release-readiness review.

## 2. Edge-Case / Failure Risks

**Risk 1 — Offline sync collisions (data integrity).**
If a mentor registers several youth offline, then multiple field staff sync from different devices around the same time, there's a risk of race conditions producing duplicate or conflicting records for the same participant (this is effectively Bug B at scale). 

**Risk 2 — USSD/SMS delivery is outside our control.**
USSD sessions can time out before a mentor finishes entering data.SMS delivery depends on telco infrastructure we don't own — congestion or spam filters or delivery failures can silently drop confirmations. A youth could be successfully registered in our system but never receive their Participant ID.

## 3. Bug Triage

Using a standard **Severity** (technical/user impact) × **Priority** (urgency to fix) framework:

| Bug | Severity | Priority | Reasoning |
|---|---|---|---|
| **A** — District dropdown renders off-screen on low-end mobile browsers | Medium | High | Doesn't corrupt data or block all users, but the target users are field mentors on low-end Android devices in rural areas, this is likely their primary device class, so it blocks registration for a large share of real-world usage. Low technical severity, high real-world priority. |
| **B** — Duplicate participant records after reconnect mid-registration | High | Critical (P0) | This is a data-integrity bug in the core feature, directly contradicts acceptance criteria #2, and duplicates corrupt downstream reporting/analytics on program enrollment. Given the field context (poor connectivity is the norm, not the exception), this will happen often. Fix before release. |
| **C** — Confirmation SMS takes up to 4 minutes instead of instant | Medium | Medium-High | Violates acceptance criterion #3 ("immediate") and hurts trust/UX, but the youth eventually get registered and receive their ID — no data is lost or corrupted. Worth fixing soon (investigate gateway/queue bottleneck) but shouldn't block release if B is resolved, since it's a degraded experience rather than a broken one. |

**Assumption noted:** I'm assuming "Severity" reflects technical/data impact and "Priority" reflects business urgency given the target users (rural field mentors, often on constrained devices network connectivity).