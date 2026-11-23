---
atom_family: SPEC
atom_id: AN-S-1158
container:
  component: C16
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 22
  updated_at: 2026-10-27 06:04:45 +0400
---
## Summary

Use a common Tool CLI interface

# Use a common Tool CLI interface

**every** Tool **must** expose the same machine-readable CLI contract for Tool kind, capability identity, help, input schema, result envelope, diagnostics, **and** exit status. **every** Finder, including **every** Checker, **must** be strictly read-only with respect **to** governed Atoms **and** Journals; **every** Doer **must** support a dry-run mode that returns its resolved targets, complete planned effects, **and** validation results **without** mutation.
