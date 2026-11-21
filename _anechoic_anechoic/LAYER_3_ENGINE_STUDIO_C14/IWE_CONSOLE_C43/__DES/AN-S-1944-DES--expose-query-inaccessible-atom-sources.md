---
atom_family: SPEC
atom_id: AN-S-1944
structure:
  container:
    component: C43
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-12T01:42:07.020152+00:00'
---

## Summary

Expose query-inaccessible Atom sources

## Claim

### Prose Claim

Expose parse and current-schema issues for the selected Atom carriers, including loaded Archive files. Record unreadable or unparseable candidates in `atom_parse_issues` even when they have no `atoms` row. Record current-schema violations in `atom_schema_issues`. Keep parseable files visible in `atoms`, and report any discrepancy between declared content and its query projection. Include the Atom identity when available, the source path, the category and the diagnostic or available location. A diagnostic must leave the source file unchanged.
