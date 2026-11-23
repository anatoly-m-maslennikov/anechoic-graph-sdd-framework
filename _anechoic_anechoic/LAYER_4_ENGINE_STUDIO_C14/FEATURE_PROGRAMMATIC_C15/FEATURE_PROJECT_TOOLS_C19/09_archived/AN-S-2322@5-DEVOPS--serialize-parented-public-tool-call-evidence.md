---
atom_family: SPEC
atom_id: AN-S-2322
container:
  component: C19
tier: 4
context:
  lens: DevOps
state:
  status: archived
  version: 5
  updated_at: 2026-10-24 02:14:24 +0400
---
## Summary

Serialize parented public Tool-call evidence

# Summary

Serialize parented public Tool-call evidence

## Scope

Tool-call evidence of one public-release Action.

## Claim

public-release Tool-call evidence **must** serialize input, result, effect, and report references under the actual parent Step and Action Run records of the existing schema-v5 Journal.

## Details

This Delivery adds neither a Tool Run kind nor a new Journal event schema. Started, terminal, and recording-pending states remain the shared schema meanings.
