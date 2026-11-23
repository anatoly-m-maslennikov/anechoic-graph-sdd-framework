---
atom_family: SPEC
atom_id: AN-S-248
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 12
  updated_at: 2026-10-24 00:28:02 +0400
---
## Summary

Reject incomplete relation-kind metadata

# Reject incomplete relation-kind metadata

## Claim checked

deterministic Tools cannot use a relation kind whose canonical registry entry is incomplete.

## Test case

compile a fixture registry containing one **otherwise** valid direct relation whose derived inverse name, declaration carrier, **or** upstream endpoint is absent, **then** gather commit context for a file using that relation.

## Acceptance criteria

registry compilation fails with the exact missing field, context gathering returns no sealed envelope, **and** no governed **or** Git state changes.

## Failure disposition

reject the registry compiler **and** Finder **if** either infers the missing field **or** continues with a partial relation entry.
