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
  version: 3
  updated_at: 2026-11-04 07:39:08 +0400
---
## Summary

Preserve Atom Header and Markdown Content faithfully in the query Projection

## Claim scope

The parsed Header and Markdown Content of every valid canonical Atom carrier.

## Claim

### Prose Claim

The query Projection **must**:

- preserve the complete parsed YAML Header, including nested mappings and lists.
- preserve the difference between an absent key, null, an empty string, an empty list or mapping, a scalar, a one-item list, false, and zero.
- preserve the complete Markdown body unchanged, including lists, links, tables, fences, fence labels, indentation, and line breaks.
- retain every mapped Content Property's complete path, heading, heading level, position, direct Markdown value and complete section Markdown; derive its parent path from the complete path.
- keep a Property's direct value separate from its descendants. A complete section includes its heading and descendants; a direct-value count does not count descendant text.
- parse YAML properties and the actual Markdown heading tree directly. The first heading may have any level; skipped levels create no synthetic Properties. Heading-like text inside code is Markdown value, not a section. Parsing does not establish Atom Form conformance or graph authority.
- reject duplicate YAML mapping keys and colliding normalized heading paths under one parent rather than silently merging or choosing one.
- not interpret arbitrary CFEL or prose to establish Projection data.
