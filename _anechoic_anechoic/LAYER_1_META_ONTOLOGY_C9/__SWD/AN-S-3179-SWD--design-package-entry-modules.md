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
  version: 3
  updated_at: "2026-11-22T09:00:09.213400+00:00"
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
- `shared` also allows the immediate parent and siblings. Use `__shared`.
- `public` allows any caller at the export boundary. Use `__pub`.

An export can add named callers to its visibility. Each cross-Package import
must satisfy the export and the applicable `boundaries.code.imports` rules.
Imports default to direct children, siblings, and public entries. A list adds
named dependencies. An `only` list restricts imports, and an empty `only` list
allows zero cross-Package imports. Keep inherited restrictions in effect.

At the first divergence in Component ancestry, when both siblings have numeric
layers, require the provider's layer to be lower. Allowlists preserve this order.

For each Package with direct authored code, prefer one direct `__shared`
entry Module. Add an optional direct `__pub` entry Module when the Package
has a Contract for external callers. Use more entry Modules when the Package
has distinct interfaces. Keep the entry Modules and implementation Modules
in the same Package directory.

## Details

In `orders/`, `orders__shared` can expose operations for the parent and
immediate sibling Packages. `orders__pub` can expose the operations in the
public Contract. `price_rules` stays Package-local. A child Package such as
`orders/validation/` owns its own Modules and entry points.

This classification applies across programming languages. A language adapter
resolves its own Module names and imports before applying the same Package
access rules.

## References

AN-S-2596, AN-S-3102, AN-S-3103, AN-S-2971, AN-S-3013, AN-S-3015,
AN-S-3016, and AN-T-2944.
