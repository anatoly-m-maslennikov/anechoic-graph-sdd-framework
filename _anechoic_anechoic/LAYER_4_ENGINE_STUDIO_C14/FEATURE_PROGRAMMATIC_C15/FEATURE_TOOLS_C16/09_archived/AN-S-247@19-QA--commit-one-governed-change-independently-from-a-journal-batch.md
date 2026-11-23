---
atom_family: SPEC
atom_id: AN-S-247
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 19
  updated_at: 2026-09-12 04:12:43 +0400
---
## Summary

Commit one governed change independently from a Journal batch

# Commit one governed change independently from a Journal batch

## Claim checked

one sealed real-change action creates **=1** Initiative-named Git commit for its governed target, while its canonical Journal record **and** **any** Journal-only batch commit remain independent evidence.

## Test case

prepare one valid `UPDATE` action with a sealed Initiative, an unrelated unstaged change, **and** an independently prepared Journal record. run the real-change gate, **then** run a later Journal batch **and** reconciliation. inspect the two commit trees, Journal record, outbox state, **and** returned envelopes.

## Acceptance criteria

the real-change commit **contains** **all** **and** **only** the resolved action target changes, no Journal carrier change, **and** the exact Initiative-based message. the unrelated change remains untouched. the Journal-only batch **contains** **only** selected Journal carrier changes **and** has the distinct batch message. reconciliation binds the same action **to** both evidence streams **without** duplicate record **or** commit.

## Failure disposition

reject the flow at the first extra commit, mixed commit class, missing action binding, message difference, duplicate Journal record, **or** unintended working-tree effect.
