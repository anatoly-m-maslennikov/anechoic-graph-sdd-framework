---
atom_family: SPEC
atom_id: AN-S-78
container:
  component: C16
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 26
  updated_at: 2026-10-26 00:46:35 +0400
---
## Summary

Commit with a live lease independently of Journal availability

# Commit with a live lease independently of Journal availability

## Claim checked

the Git Doer **may** commit a governed real-change action while its Journal record is absent, pending, **or** already appended, but it cannot commit **without** the live repository lease **and** exact sealed action boundary.

## Test case

Invoke `COMMIT_CHANGE_SET` for one current sealed real-change action with a live matching lease while its Journal state is respectively absent, pending, **and** appended. Repeat with a missing, stale, released, **or** different-action repository lease. Then append the Journal record **and** commit it **in** a later Journal-only batch.

## Acceptance criteria

Each valid Journal-state case creates the same exact real-change commit **without** requiring **or** staging a Journal carrier. Each invalid lease produces a stable diagnostic **before** staging **or** commit creation **and** does **not** release **or** alter another action's lease. The later Journal record binds the real-change commit identity **and** its Journal-only commit **contains** **only** selected Journal carriers.

## Failure disposition

Reject the Git Doer **if** Journal availability gates a valid real-change commit, **if** it commits **without** the live matching lease **and** exact sealed target set, **if** it mixes a Journal carrier into the real-change commit, **or** **if** delayed Journal append **or** batching loses **or** duplicates provenance.
