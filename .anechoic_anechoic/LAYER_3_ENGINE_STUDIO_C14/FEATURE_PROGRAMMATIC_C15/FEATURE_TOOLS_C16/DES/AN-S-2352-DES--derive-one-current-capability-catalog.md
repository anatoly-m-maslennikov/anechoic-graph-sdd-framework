---
identity:
  atom_id: AN-S-2352
context:
  container:
    component: C16
  tier: 3
  lens: DES
state:
  status: active
  version: 12
  updated_at: 2026-10-27 20:00:03 +0400
---
## Summary

Derive one current capability catalog

## Scope

the TOOLS capability for Capability Catalog.

## Claim

### Prose Claim

the Capability Catalog **must** be **`=1`** derived read model shared by Tool discovery, Operations discovery **and** execution-context retrieval.

## Details

- active source Atoms **and** authoritative Project Structure declare capabilities **and** scope ancestry.
- D-owned Tool bindings declare Implementation paths **and** Action bindings; observed files **and** registered MCP handlers establish observed availability.
- declared authority, observed Implementation **and** exposed execution are distinct facts.
- source changes invalidate the derived catalog. duplicate active identifiers, ambiguous bindings, malformed sources **and** bounded reads remain visible.
- the catalog is a Projection; its descriptions do **not** become a separately authored source of truth.
