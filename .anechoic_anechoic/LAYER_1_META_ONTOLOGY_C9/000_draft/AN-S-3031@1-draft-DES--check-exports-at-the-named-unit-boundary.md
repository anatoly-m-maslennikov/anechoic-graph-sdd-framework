---
atom_family: SPEC
atom_id: AN-S-3031
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:05:18.738009+00:00'
---
## Summary

Check exports at the named Unit boundary

## Claim

### Prose Claim

A Unit-level export allows callers to import the named Unit directly. A caller importing the containing Module requires a Module-level export. Check each named import against its own export, provider visibility, applicable caller rules, and the layer direction in CA-R-3169.

## Details

Acceptance: when only `billing.api.run` is exported and the caller is otherwise allowed, accept `from billing.api import run` and reject an import of `billing.api` as a Module.

Sources: CA-A-1463@1-draft. Task: CA-P-3084.
