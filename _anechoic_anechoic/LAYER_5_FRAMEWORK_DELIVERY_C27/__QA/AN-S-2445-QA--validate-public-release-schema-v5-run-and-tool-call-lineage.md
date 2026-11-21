---
atom_family: SPEC
atom_id: AN-S-2445
structure:
  container:
    component: C27
  tier: 4
context:
  lens: QA
state:
  status: active
  version: 11
  updated_at: 2026-11-09 15:54:30 +0400
---

## Summary

Validate public-release schema-v5 Run and Tool-call lineage

## Scope

the Journal output of one public-release fixture.

## Claim

### Prose Claim

**the Operator** **must** verify schema-v5 actual Workflow, Step, and Action Run parentage, started and terminal records, and Tool-call evidence references parented to their Step and Action without any Tool Run kind.

## Details

The check rejects source claims of success without durable Run evidence.
