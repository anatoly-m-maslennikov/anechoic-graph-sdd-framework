---
atom_family: SPEC
atom_id: AN-S-7
container:
  component: C16
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 27
  updated_at: 2026-10-24 23:55:59 +0400
---
## Summary

Classify file removal as REMOVE

# Classify file removal as REMOVE

## Claim checked

removal of a governed file identity with no resulting Carrier for that file is classified as `REMOVE`. disappearance from the active address alone does **not** establish removal **when** the file moved **to** another address, including an archive.

## Test case

supply a sealed observation whose preceding graph **contains** the governed file **and** whose candidate result has no Carrier for that file identity. separately include an unchanged file relocated **to** an archive as a control. observe **any** existing Git index separately; context gathering **must not** stage **or** remove files.

## Acceptance criteria

- the removal context reports `REMOVE` **and** emits the removed-state result with filename **and** Version, **without** present-only path **or** Digest.
- previous_result_event refers **to** the immediate preceding present result; authored Relations are resolved from the last committed graph **without** copying redundant before-state fields into the result.
- the archive control is classified as `MOVE` rather than `REMOVE`. historical evidence **and** replacement IDs, **when** applicable, retain their separate registered Journal rules.
- no classification changes the Project **or** certifies conformance of the observed removal.

## Failure disposition

reject an incorrect change class, malformed tombstone, missing predecessor reference, lost observation, copied before-state field, mutation **or** incorrect Relation source.
