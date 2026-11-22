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
  version: 4
  updated_at: "2026-11-22T14:32:45.806649+00:00"
---

## Summary

Design Package entry Modules

## Claim

### Prose Claim

A Package is a logical group of owned Modules or nested Packages. In a file-based
Realization, a directory carries the Package. Use the declared ownership to
identify the Package, its parent, and its siblings. Evaluate each Package
separately. A folder with only child Packages does not need an entry Module for
their code.

A Component Package is the Realization Package of a Component. An ordinary
Package becomes a Component Seed when it gets a Component Seed Manifest.

Declare Module or symbol exports in `boundaries.code.exports`. Unlisted entries
are private to the owning Package. When the export map is absent, use the Module
marker. An explicit export with omitted visibility is shared.

- `private` allows the owning Package.
- `shared` also allows the immediate parent and siblings.
- `public` allows any caller at the export boundary.

An export can add named callers to its visibility. Each cross-Package import
must satisfy the export and the applicable `boundaries.code.imports` rules.
Imports default to direct children, siblings, and public entries. A list adds
named dependencies. An `only` list restricts imports, and an empty `only` list
allows zero cross-Package imports. Keep inherited restrictions in effect.

At the first divergence in Component ancestry, when both siblings have numeric
layers, require the provider's layer to be lower. Allowlists preserve this order.

Give each Package with direct authored code exactly one direct
`__shared` entry Module. Apply the rule to Component Packages, Component
Seeds, ordinary nested Packages, and Test Packages. Put the entry Module
and implementation Modules in the same Package directory.

An import from another Package must target the entry Module and comply
with Code Access. Declare shared, public, and named exports on that
Module. Implementation Modules are private to the Package.

## Details

In `orders/`, `orders__shared` can expose shared Order operations and
declare public exports for the operations in the Contract. `price_rules`
stays Package-local. A child Package such as `orders/validation/` has
its own `validation__shared` entry Module.

This classification applies across programming languages. A language adapter
resolves its own Module names and imports before applying the same Package
access rules.

## References

AN-S-2596, AN-S-3102, AN-S-3103, AN-S-2971, AN-S-3013, AN-S-3015,
AN-S-3016, and AN-T-2944.
