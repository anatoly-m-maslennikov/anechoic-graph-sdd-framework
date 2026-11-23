---
atom_family: SPEC
atom_id: AN-S-1101
container:
  component: C16
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 16
  updated_at: 2026-10-24 22:06:39 +0400
---
## Summary

Verify extract one extension candidate from project adaptation

# Verify extract one extension candidate from project adaptation

## Claim checked

CA-M-216 extracts one independently identified Extension candidate with a complete attributable reusable dependency boundary.

## Applicable when

apply whenever Project Adaptation extraction **or** dependency-closure rules change.

## Test case

select two Project Adaptation Atoms whose required dependency closure includes one transitive dependency **and** one unresolved required dependency. extract, **then** resolve the missing dependency with an exact source reference **and** repeat.

## Acceptance criteria

the unresolved attempt produces no candidate; the resolved attempt includes the selected Atoms **and** complete transitive closure with exact revisions **and** one stable candidate identity.

## Failure disposition

reject the extraction method **and** preserve selection, closure graph, unresolved dependencies, source revisions, emitted candidate manifest, **and** proof that source authority was unchanged.
