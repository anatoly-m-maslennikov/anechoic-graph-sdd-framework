---
atom_family: SPEC
atom_id: AN-S-2390
container:
  component: C16
tier: 5
context:
  lens: DevOps
state:
  status: archived
  version: 8
  updated_at: 2026-10-24 09:42:52 +0400
---
## Summary

Place shared selected Run support at the existing TOOLS boundary

# Summary

Place shared selected Run support at the existing TOOLS boundary

## Scope

Implementation placement for the shared service and its existing Journal
dependency. No new Scope Unit, executable Tool, workflow, or Journal is
declared by this Delivery.

## Claim

Shared selected-Run support **must** be delivered as the non-executable library
`102_FRAMEWORK_ENGINE/201_PROGRAMMATIC/201_TOOLS/workflow_run_support.py`,
beside the existing non-executable `work_journal.py`, and callers must use that
one library rather than adapter-local Run/Journaling implementations.

## Details

- The library owns only request validation, currentness admission, Run
  provenance shaping, pending-recording recovery, and use of `work_journal`.
  Selected route executors, MCP adapters, and prompt/runtime components retain
  their existing ownership and inject their effects/results through the shared
  contract.
- Its only durable historical authority is the Project Work Journal configured
  by Project settings. Its runtime pending/receipt state is under the existing
  `.anechoic_runtime/state/work_journal/` boundary and must not be projected
  as a competing Journal.
- No caller receives an implicit worker start, background run, new source
  campaign, or authority to mutate from importing the library. A later
  separately approved delivery may add route implementations only after this
  RMED packet has independent review.
