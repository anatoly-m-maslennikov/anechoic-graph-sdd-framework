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
  version: 1
  updated_at: 2026-11-03 23:17:14 +0400
---
## Summary

Preserve Atom Header and Markdown Content faithfully in the query Projection

## Claim scope

The indexed Header and Content of every valid canonical Atom carrier.

## Claim

### Prose Claim

The query Projection **must**:

- preserve the complete parsed YAML Header and original frontmatter text, including nested mappings and lists.
- preserve the difference between an absent key, null, an empty string, an empty list or mapping, a scalar, a one-item list, false, and zero.
- preserve the complete Markdown body unchanged, including lists, links, tables, fences, fence labels, indentation, and line breaks.
- retain every mapped Content Property's complete path, parent path, heading, heading level, position, direct Markdown value, and complete section Markdown.
- keep a Property's direct value separate from its descendants. A complete section includes its heading and descendants; a direct-value count does not count descendant text.
- use actual Markdown heading structure. Heading-like text in a code fence or in an undeclared child position remains Markdown value, and skipped heading levels create no Properties.
- reject duplicate YAML mapping keys and colliding normalized heading paths under one parent rather than silently merging or choosing one.

