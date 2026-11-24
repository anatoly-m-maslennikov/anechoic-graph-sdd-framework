---
atom_family: SPEC
atom_id: AN-S-3179
container:
  component: C9
tier: 3
context:
  lens: SWD
state:
  status: active
  version: 8
  updated_at: "2026-11-23T01:48:06.192387+00:00"
---
## Summary

Design Package entry Modules

## Claim

### Prose Claim

Use declared ownership to identify each Package, its parent, and its siblings. Every Package with direct authored code has one direct `__shared` Module, including Component Packages, Seeds, nested Packages, and Test Packages. A directory that only groups child Packages needs no entry of its own.

Use the defining Package's entry to import its symbols. Declare exact exports and restrictions in `boundaries.code`. Qualify nested entries by their path in the owning Component Manifest. By default an unlisted Module is private and an explicit export with omitted visibility is shared. Without an export map, use the Module marker.

- `private` allows the owning Package.
- `shared` also allows its immediate parent and siblings.
- `public` allows any caller at the export boundary.

A caller must also satisfy `boundaries.code.imports`. Default imports reach direct children, siblings, and public entries. An addition names extra dependencies. `only` limits the set. Preserve inherited restrictions and import toward the lower layer at the first divergence between layered siblings.

Record each implementation-Module bypass by exact Module or symbol in imports and exports. Check it against the same visibility and layer rules. Repeated bypasses signal that the owner may need promotion. A Package may expose an operation it owns and keep foreign symbols inside. Forwarding another Package's symbol through a wrapper does not establish ownership.

## References

AN-S-3013, AN-S-3014, and AN-S-3347.
