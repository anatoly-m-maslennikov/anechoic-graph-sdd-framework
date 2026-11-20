---
identity:
  atom_id: AN-S-1158
context:
  container:
    component: C16
  tier: 1
  lens: DES
state:
  status: active
  version: 24
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Use a common Tool CLI interface

# Use a common Tool CLI interface

**every** Tool **must** expose the same machine-readable CLI contract for Tool kind, capability identity, help, input schema, result envelope, diagnostics, **and** exit status. **every** Finder, including **every** Checker, **must** be strictly read-only with respect **to** governed Atoms **and** Journals; **every** Doer **must** support a dry-run mode that returns its resolved targets, complete planned effects, **and** validation results **without** mutation.
