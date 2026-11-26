---
atom_family: SPEC
atom_id: AN-S-3179
container:
  component: C9
tier: 3
context:
  lens: SWD
state:
  status: "active"
  version: 11
  updated_at: "2026-11-25T19:21:20.633573+00:00"
---
## Summary

Design Package entry Modules

## Claim

### Prose Claim

Use declared ownership to identify each Package, parent, and siblings. Qualify nested entries by their path in the owning Component Manifest. Import each symbol through the entry of the Package that defines it.

Apply the entry and visibility rules of the Implementation Package Manifest. Production Packages cannot import from Test Packages.

Declare overrides in the applicable Manifest. A caller lists additions in `boundaries.code.imports`. An `only` list limits the caller and inherited `only` lists all apply. An exact Module or symbol selector is required to import through an implementation Module.

Repeated bypasses signal that the owner may need promotion. A Package may expose an operation it owns and keep foreign symbols inside. Import a symbol from the Package that defines it. Forwarding another Package's symbol through a wrapper does not establish ownership.

## References

AN-S-3013, AN-S-3014, and AN-S-3347.
