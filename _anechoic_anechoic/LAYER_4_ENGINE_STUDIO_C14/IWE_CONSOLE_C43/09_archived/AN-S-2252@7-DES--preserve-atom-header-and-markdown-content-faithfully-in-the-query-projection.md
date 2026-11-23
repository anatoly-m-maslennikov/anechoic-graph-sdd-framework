---
atom_family: SPEC
atom_id: AN-S-2252
container:
  component: C43
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 7
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Preserve Atom Header and Markdown Content faithfully in the query Projection

## Claim scope

The parsed Header and Markdown Content of every valid canonical Atom carrier.

## Claim

### Prose Claim

The Projection preserves complete parsed YAML Header and Markdown body, including nested mappings/lists, lists/links/tables/fences/indentation/line breaks, actual heading paths and complete mapped Content sections. It distinguishes absent/null/empty scalar-or-collection/false/zero; display metadata treats null/empty string/list/map as empty while false/zero remain values without changing SQL values/counts.

Mode 1 exposes model-declared Header paths; enabled Mode 2 exposes every observed valid Header path, including null/empty. Both use dotted full Header paths with snake_case segments and remove short `id`/`role`/`status` aliases; Header has no wrapper or flat copy. Declared Content paths use the same notation, preserve parent direct value separately from nested Properties, and arbitrary presentation headings never become columns. Complete parser data remains private: `atoms` exposes no raw Header/Markdown/property/relation JSON buckets.

Parse YAML and the actual CommonMark tree directly: no Form conformance or graph authority, synthetic skipped-level Properties or fenced-text headings. Reject duplicate YAML keys and colliding normalized declared child headings; allow repeated arbitrary prose headings. Never interpret arbitrary CFEL or prose as Projection data.
