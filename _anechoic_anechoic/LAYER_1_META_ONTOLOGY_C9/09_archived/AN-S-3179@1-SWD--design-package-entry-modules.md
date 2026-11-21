---
atom_family: SPEC
atom_id: AN-S-3179
container:
  component: C9
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 1
  updated_at: '2026-11-21T12:43:52.360824+00:00'
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
Package belongs to a Component and can have its own Package Spec. A Component
Seed is the proposed name for that specified ordinary Package.

Use these three visibility levels for Package Modules:

- **Package-local**. Only Modules in the owning Package can import the Module.
  This is the default for unmarked Modules. In prose, use private for this
  access level when the Package scope is clear.
- **Package-family public**. The owning Package, its immediate parent,
  and its immediate sibling Packages can import the entry Module. Mark the
  filename with `__family_pub` before the file extension. AN-S-3015 calls this
  scope Internal. A root Package has no parent or siblings.
- **Public**. Callers beyond the Package family can import an eligible entry
  Module. Mark the filename with `__pub` before the file extension.

For each Package with direct authored code, prefer one direct `__family_pub`
entry Module. Add an optional direct `__pub` entry Module when the Package
has a Contract for external callers. Use more entry Modules when the Package
has distinct interfaces. Keep the entry Modules and implementation Modules
in the same Package directory.

Each import must also pass the applicable caller rules. When a Package declares
an explicit export list in SPEC, use that list for cross-Package access.

## Details

In `orders/`, `orders__family_pub` can expose operations for the parent and
immediate sibling Packages. `orders__pub` can expose the operations in the
public Contract. `price_rules` stays Package-local. A child Package such as
`orders/validation/` owns its own Modules and entry points.

This classification applies across programming languages. A language adapter
resolves its own Module names and imports before applying the same Package
access rules.

## References

AN-S-2596, AN-S-3102, AN-S-3103, AN-S-2971, AN-S-3013, AN-S-3015,
AN-S-3016, and AN-T-2944.
