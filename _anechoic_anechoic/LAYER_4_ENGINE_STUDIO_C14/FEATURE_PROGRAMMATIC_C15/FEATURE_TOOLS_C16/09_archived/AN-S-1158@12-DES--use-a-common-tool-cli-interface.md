---
atom_family: SPEC
atom_id: AN-S-1158
container:
  component: C16
tier: 4
context:
  lens: DES
state:
  status: archived
  version: 12
  updated_at: 2026-08-30 16:44:07 +0400
---
## Summary

Use a common Tool CLI interface

# Use a common Tool CLI interface

**every** Tool **must** expose the same machine-readable CLI contract for Tool kind, capability identity, help, input schema, result envelope, diagnostics, **and** exit status. **every** Finder, including **every** Checker, **must** be strictly read-only with respect **to** governed Atoms **and** Journals; **every** Doer **must** support a dry-run mode that returns its resolved targets, complete planned effects, **and** validation results **without** mutation.
