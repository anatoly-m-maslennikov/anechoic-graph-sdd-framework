---
atom_family: SPEC
atom_id: AN-S-92
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 14
  updated_at: 2026-10-24 00:28:02 +0400
---
## Summary

Route by the sealed Journal date

# Route by the sealed Journal date

## Claim checked

the Journal-appending Doer routes an event by the author **and** local date sealed **in** its context, even **when** the current clock has crossed a calendar boundary.

## Test case

**in** `Asia/Tbilisi`, seal one context at `2026-08-20 23:59:59 +04`, advance the controlled clock **to** `2026-08-21 00:00:01 +04`, **and** apply the unchanged sealed event.

## Acceptance criteria

the event is appended once **to** `<author>-2026-08-20-part-<N>.ndjson`; its stored `occurred_at` remains unchanged; **and** no carrier for `2026-08-21` is created for that event.

## Failure disposition

reject the Doer **if** it recomputes author, date, timezone, **or** `occurred_at`, routes by the current clock **or** filesystem time, **or** appends the event more than once.
