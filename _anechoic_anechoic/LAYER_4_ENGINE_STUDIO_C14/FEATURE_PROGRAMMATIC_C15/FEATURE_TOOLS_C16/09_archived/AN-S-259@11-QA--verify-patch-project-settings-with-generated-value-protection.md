---
atom_family: SPEC
atom_id: AN-S-259
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 11
  updated_at: 2026-10-24 00:28:02 +0400
---
## Summary

Verify patch project settings with generated-value protection

# Verify patch project settings with generated-value protection

## Claim checked

CA-M-212 changes **only** schema-editable Project Settings keys **and** rejects generated, unknown, **or** stale targets.

## Applicable when

apply whenever the Project Settings schema, ownership classification, **or** patch mechanics change.

## Test case

seal one settings carrier **and** request changes **to** one schema-editable key, one generated key, **and** one unknown key. observe rejection, **then** apply **only** the editable change **and** compare **every** key **and** byte-level diff.

## Acceptance criteria

the mixed patch changes nothing **and** identifies both prohibited keys; the valid patch changes exactly the editable key, preserves **all** unrelated **and** generated values, remains schema-valid, **and** has no undeclared diff.

## Failure disposition

reject the realization **and** preserve schema, key classifications, requested operations, dry-run diff, final carrier, **and** undeclared-change comparison.
