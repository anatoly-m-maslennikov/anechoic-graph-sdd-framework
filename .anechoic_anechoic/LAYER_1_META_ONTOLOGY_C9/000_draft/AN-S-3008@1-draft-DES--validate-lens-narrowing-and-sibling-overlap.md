---
identity:
  atom_id: AN-S-3008
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:04:53.919864+00:00'
---
## Summary

Validate lens narrowing and sibling overlap

## Claim

### Prose Claim

Lenses use the `narrower_than` relation; every other lens is narrower than SPEC. A broader lens and any selection of its narrower lenses may be enabled together, but a narrower lens is separately available only when listed in the effective whitelist. Enabled sibling lenses must have disjoint sets of detailed lenses. Reject a whitelist when enabled siblings overlap; do not infer overlap merely because a broader lens is enabled with one of its narrower lenses.

## Details

Acceptance: `[SPEC, DES, SWE]` is valid; `[SWE, SWD, QA]` is valid and does not enable omitted DevOps. Given DES expands to IO and DOM and SYS expands to SWE and DOM, `[DES, SYS]` is invalid because both contain DOM. The same lens expansion applies in every Component.

Sources: CA-A-1462@1-draft, CA-P-3081@1. Task: CA-P-3081.
