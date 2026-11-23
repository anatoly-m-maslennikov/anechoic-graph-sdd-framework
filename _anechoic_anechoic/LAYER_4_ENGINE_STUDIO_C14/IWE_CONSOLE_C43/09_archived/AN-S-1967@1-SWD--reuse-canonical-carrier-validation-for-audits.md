---
atom_family: SPEC
atom_id: AN-S-1967
container:
  component: C43
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 1
  updated_at: 2026-11-11 00:34:40 +0400
---

## Summary

Reuse canonical carrier validation for audits

## Claim

### Prose Claim

Reuse the existing source reader, locator and canonical carrier validation for all three Workbench audit tables. Generate the audit rows from the same selected Current and Draft source scan and the same canonical identity and path values. Reuse existing invalid and unreadable-source diagnostics. Do not add a second reader, a separate consistency Action or source mutation. Keep the tables query-visible and side-effect-free.

