---
atom_family: SPEC
atom_id: AN-S-3885
container:
  component: C21
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 14
  updated_at: 2026-10-26 00:46:35 +0400
---
## Summary

Reject registry publication for one invalid Tool projection

# Reject registry publication for one invalid Tool projection

## Claim checked

An invalid selected Tool projection prevents publication of a partial current registry.

## Test case

Introduce one source Tool with an invalid schema into an **otherwise** valid selected frontier.

## Acceptance criteria

No new registry is published **and** the invalid source receives an explicit diagnostic.

## Failure disposition

Preserve the defect for repair; do **not** silently skip it.
