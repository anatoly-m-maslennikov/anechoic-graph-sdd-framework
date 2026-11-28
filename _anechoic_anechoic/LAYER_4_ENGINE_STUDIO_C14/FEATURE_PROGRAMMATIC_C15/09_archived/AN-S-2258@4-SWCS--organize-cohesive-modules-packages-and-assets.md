---
atom_family: SPEC
atom_id: AN-S-2258
container:
  component: C15
tier: 1
context:
  lens: SWD/SWCS
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-27T20:35:14.221449+00:00"
---
## Summary

Organize cohesive modules, packages and assets

## Claim scope

New or materially changed hand-authored PROGRAMMATIC implementation, including code modules, packages, tests and owned non-code source assets throughout descendant Scope Units. This Method owns shared cohesion, package organization and source-asset rules. Applicable language-specific source-size rules keep their own authority.

## Claim

### Prose Claim

Organize implementation around cohesive responsibilities:

- Each class, function and module has one cohesive responsibility. Review responsibility separately from numeric size.
- A helper is meaningful only when it expresses a reusable responsibility or boundary. Do not add helpers, wrappers, indirection, line compression or formatting changes merely to game a threshold.
- Growing implementation is split into cohesive packages or subfolders with visible ownership, not a sprawling flat file set or meaningless nesting.
- Descriptive, sufficiently verbose filenames identify module responsibility. Preserve platform-required names and locations.
- JSON, YAML, TOML and other owned source assets belong in the owning module's local `assets/` folder unless a platform requires another name or location. Governed Atom carriers, Journals and Runtime outputs are not implementation source assets. RMEDO trace sidecars follow their own placement policy and sit beside the module or at the package root.

Apply the relevant source-size and measurement rules to their declared language and source boundary. Do not turn Python limits into limits for every language or weaken the separate frontend limits. An unresolved policy conflict remains unresolved; do not invent a shared number.

## Details

Apply this Method to new or materially changed hand-authored source. Vendor code, generated output, frozen fixtures and legacy history remain outside automatic migration.

Preserve dependency direction and testability when extracting helpers or splitting packages. Do not split a cohesive class merely to satisfy a count, or use class size to excuse an oversized or incohesive method under its applicable policy. Source assets stay with their owner; governed Carriers, Journal records and Runtime outputs keep their existing boundaries.
