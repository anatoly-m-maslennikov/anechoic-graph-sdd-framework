---
atom_family: SPEC
atom_id: AN-S-2593
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 8
  updated_at: "2026-11-25T23:05:48.090106+00:00"
---

## Summary

Declare CFEL PATH_TEMPLATE

## Claim

### Prose Claim

`PATH_TEMPLATE([string])` returns one repository-relative directory path for the selected Atom. Its argument is a quoted template. A named component occupies a complete segment.

- `<owning scope unit>` resolves to the owning Scope Unit directory.
- `<role folder>` resolves to the legacy Role folder derived under AN-S-2136@34.
- `<container>` resolves to the Scope Unit's Role directory or the containing Atom's matching Directory Carrier.
- `<status folder>` resolves to the folder name for the selected historical Status under AN-S-1918@1.
- `<placement>` resolves to the directory suffix selected by the applicable Status rule. Omit that segment when the suffix is empty.

A Role template combines the derived Role folder with the applicable Status placement. Resolve that Status template before substituting `<placement>`. A specific Status rule takes precedence over the Status Group rule. A Role-qualified Status rule takes precedence over the same Status rule without a Role. The resolved path contains no unresolved components, absolute prefix or parent-directory traversal.
