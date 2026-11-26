---
atom_family: SPEC
atom_id: AN-S-3179
container:
  component: C9
tier: 3
context:
  lens: SWD
state:
  status: "archived"
  version: 10
  updated_at: "2026-11-24T23:09:17+00:00"
---
## Summary

Design Package entry Modules

## Claim

### Prose Claim

Use declared ownership to identify each Package, its parent, and its siblings. Every Package with direct authored code has one direct `__shared` Module, including Component Packages, Seeds, nested Packages, and Test Packages. A directory that only groups child Packages needs no entry of its own.

Use the defining Package's entry to import its symbols. Qualify nested entries by their path in the owning Component Manifest. A direct entry Module with a `__shared`, `__family_pub`, or `__internal` marker is shared. A direct entry Module with a `__pub` or `__public` marker is public. An unmarked implementation Module needs an exact caller declaration.

A shared entry is available by default to its owning Package, direct child, and sibling Packages. A public entry is available to any caller unless an inherited closed `only` rule denies it. A selector naming the provider Component grants its shared entries.

For Code Access, a Package is a Test Package if any segment of its Project-relative path ends in `__tests`. A non-test Package must not import from a Test Package. This rule takes precedence over all other Code Access permissions.

A caller declares dependencies in `boundaries.code.imports`. A list adds selectors. `only` closes the inherited set, and every inherited closed rule must match. An exact Module or symbol selector is required for an implementation-Module bypass. Check the bypass against the same visibility and layer rules.

At the first divergence in Component ancestry, when both layers are numeric, an import can target only the lower-layer provider. This is the upstream direction for ordered siblings.

Repeated bypasses signal that the owner may need promotion. A Package may expose an operation it owns and keep foreign symbols inside. Import a symbol from the Package that defines it. Forwarding another Package's symbol through a wrapper does not establish ownership.

## References

AN-S-3013, AN-S-3014, and AN-S-3347.
