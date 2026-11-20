---
identity:
  atom_id: AN-T-1036
context:
  container:
    component: C45
  tier: 4
  template: problem
state:
  status: active
  version: 1
  updated_at: 2026-11-10 04:02:58 +0400
---

## Summary

Valid serialized Role values lose declared query content

## Concern

The content reader compares Role/Form strings exactly against business-spelled Declaration filters. Current M514/M515 use the admitted lower_snake_case carrier values `method` and `direct_policy`, so their correct Prose Claims are not exposed by the compiled content schema. The newly prepared normalized Drafts hit the same boundary.

## Details

Preserve the valid source serialization. Verify and fix the common reader/schema adaptation before promotion; do not rewrite source values to conceal the mismatch. The local reader reproduced the gap. No deployed-service failure or code fix is claimed.
