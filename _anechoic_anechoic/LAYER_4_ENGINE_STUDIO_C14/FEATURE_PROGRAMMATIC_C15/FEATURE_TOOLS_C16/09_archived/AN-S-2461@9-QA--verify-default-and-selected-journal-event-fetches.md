---
atom_family: SPEC
atom_id: AN-S-2461
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 9
  updated_at: 2026-10-27 06:04:45 +0400
---
## Summary

Verify default and selected Journal Event fetches

# Summary

Verify default and selected Journal Event fetches

## Claim

The Tool returns only Event IDs by default and returns only explicitly selected fields or full Events when requested.

## Test case

Query one snapshot in default, selected-field, full-Event, and missing-selected-field modes.

## Acceptance criteria

Default records contain only canonical IDs; selected mode preserves requested field order; full mode preserves Event content; missing values remain explicit diagnostics.

## Failure disposition

Reject unrequested Event content, filename IDs, or synthesized missing values.
