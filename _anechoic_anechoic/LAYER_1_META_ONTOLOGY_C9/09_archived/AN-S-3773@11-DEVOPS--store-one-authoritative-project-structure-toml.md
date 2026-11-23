---
atom_family: SPEC
atom_id: AN-S-3773
container:
  component: C9
tier: 1
context:
  lens: DevOps
state:
  status: archived
  version: 11
  updated_at: 2026-10-24 01:37:42 +0400
---
## Summary

Store one authoritative Project Structure TOML

# Summary

Store one authoritative Project Structure TOML

## Scope

the authoritative Project Structure Carrier.

## Claim

the authoritative Project Structure Carrier **must** be **`=1`** UTF-8 TOML file named `project_structure.toml` directly inside the owning `.anechoic_<project_name>/` directory. `<project_name>` resolves from the owning Project Settings. this non-Atom Carrier **must not** carry an Atom ID, Atom Content Role, Atom Frontmatter, **or** non-authoritative Projection metadata. concrete unit paths belong **only** **to** this file, while Delivery Atoms retain general Carrier schema **and** representation authority.

## Details
