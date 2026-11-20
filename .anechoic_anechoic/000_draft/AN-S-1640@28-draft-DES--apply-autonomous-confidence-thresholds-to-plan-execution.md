---
atom_family: SPEC
atom_id: AN-S-1640
structure:
  container:
    component: C00
  tier: 2
context:
  lens: DES
state:
  status: draft
  version: 28
  updated_at: 2026-11-02 18:35:20 +0400
---
## Summary

Apply autonomous confidence thresholds to Plan execution

## Claim scope

autonomous continuation of Plan work.

## Claim

autonomous continuation of Plan work **must** satisfy its effective Autonomous Confidence Threshold:

- resolve the value under CA-M-271-CORE_META_MODEL-IMPLEMENTATION_METHOD--resolve-confidence-thresholds-by-source-precedence.
- **if** confidence **in** correct execution is below it, request Operator disposition **before** continuing.
- **otherwise**, continue **only** within existing authority; meeting the threshold does **not** grant additional authority.
