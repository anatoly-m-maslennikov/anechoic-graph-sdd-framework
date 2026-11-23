---
atom_family: SPEC
atom_id: AN-S-82
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 14
  updated_at: 2026-10-24 00:28:02 +0400
---
## Summary

Reject a noncanonical governed commit message

# Reject a noncanonical governed commit message

## Claim checked

the Git gate accepts a real-change message **only** **when** it is the Initiative-based Projection for its sealed action.

## Test case

For one valid atomic action, present the exact `<initiative-summary> | <CHANGE_CLASS> | <affected-subject>` message **and** variants with a technical parent, changed class, changed subject, extra body line, **or** trailer. Separately present the Journal-batch form for a real-change action.

## Acceptance criteria

**only** the exact real-change Projection succeeds. Every altered **or** Journal-batch form fails **before** the Git effect **without** changing the message carrier, index, working tree, governed source, Journal, refs, **or** runtime state.

## Failure disposition

Reject the delivery **if** a noncanonical message passes, the canonical message fails, **or** message validation mutates project state.
