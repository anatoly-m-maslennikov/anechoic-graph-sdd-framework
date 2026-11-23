---
atom_family: SPEC
atom_id: AN-S-3594
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-05 00:30:00 +0400
---
## Summary

Bind Journal query to declared Tool and golden-test paths

# Summary

Bind Journal query to declared Tool and golden-test paths

## Scope

The query implementation location.

## Claim

FIND_AND_FETCH_JOURNAL_EVENTS **must** be delivered only at `102_FRAMEWORK_ENGINE/201_PROGRAMMATIC/201_TOOLS/FIND_AND_FETCH_JOURNAL_EVENTS/` with its golden test at `102_FRAMEWORK_ENGINE/201_PROGRAMMATIC/201_TOOLS/FIND_AND_FETCH_JOURNAL_EVENTS/tests/test_find_and_fetch_journal_events.py`.

## Details

This declaration does not create the implementation or register an MCP route.
