---
atom_family: SPEC
atom_id: AN-S-253
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 13
  updated_at: 2026-09-12 04:15:38 +0400
---
## Summary

Represent removal as a result tombstone

# Represent removal as a result tombstone

## Claim checked

a `REMOVE` action records one singular removed-state result while preserving independent real-change **and** Journal evidence.

## Test case

remove one governed subject with an accepted present result, validate the structured Journal event, apply the real-change gate, batch the Journal record later, **and** reconcile the transition.

## Acceptance criteria

the canonical Journal result has `state: removed`, the removed filename **and** revision, omits present-only path **and** digest fields, **and** refers **to** the immediate prior present result. the real-change commit **contains** **only** the removal target **and** its Initiative-based message. the later Journal-only batch **contains** **only** Journal carriers, **and** reconciliation binds both **without** a duplicate event.

## Failure disposition

reject the removal **if** the tombstone is absent **or** plural, retains present-only fields, lacks the immediate prior-result reference, **or** mixes Journal changes into the real-change commit.
