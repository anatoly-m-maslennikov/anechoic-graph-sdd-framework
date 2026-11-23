---
atom_family: SPEC
atom_id: AN-S-2378
container:
  component: C16
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 5
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

Journal only an actual query Run through shared support

# Summary

Journal only an actual query Run through shared support

## Scope

Actual query invocation evidence.

## Claim

To record an actual Journal query invocation, the Tool **must** delegate
preview/execute admission and Run evidence to shared selected-Run support only
after the adapter captured the sealed frontier; that evidence consumes no Event
in the frontier.

## Details

Preview has no Run/Event; execute records only actual Run outcomes and cannot change the already captured result frontier.
