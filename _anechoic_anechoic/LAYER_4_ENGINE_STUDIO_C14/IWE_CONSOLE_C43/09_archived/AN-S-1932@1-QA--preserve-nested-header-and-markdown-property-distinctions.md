---
atom_family: SPEC
atom_id: AN-S-1932
container:
  component: C43
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 1
  updated_at: 2026-11-03 23:17:14 +0400
---
## Summary

Preserve nested Header and Markdown Property distinctions

## Claim scope

The Atom reader and its DuckDB projection of one governed source carrier.

## Claim

### Prose Claim

The projection passes when it preserves the source path and bytes, the complete
parsed Header, the original frontmatter text, and the complete Markdown body
without changing their meaning.
Header values remain distinct for an absent key, YAML null, empty string, empty
list, empty mapping, scalar, one-item list, false, and zero. Duplicate mapping
keys are rejected. Mapped Markdown Properties retain their path, parent, heading,
level, position, direct value, and complete section. A section's direct value is
not replaced by, or joined with, its child sections. Claim, Prose Claim, and
Formal Claim remain distinct; headings in fenced code or admitted Prose Claim
text do not become child Properties. Equal normalized sibling headings fail,
while equal names under different parents remain separate paths.

## Details

### Fixtures and expected outcomes

| Fixture | Expected outcome |
| --- | --- |
| Header entries covering absence, null, empty string, empty list, empty mapping, scalar, one-item list, false, and zero | Every value remains queryably distinct; no value is coerced into another form. |
| Header with a duplicate mapping key | The carrier is rejected with a source error; the last key does not silently win. |
| Markdown section with direct text and a child section | The parent exposes its direct Markdown and its complete section separately; the child is not concatenated into the direct value. |
| `Claim` containing `Prose Claim` and `Formal Claim` | `Claim` has both child paths, preserves each child's heading and value, and keeps the CFEL fence in `Formal Claim`; the container is not treated as a joined direct value. |
| Skipped heading levels, a heading-like line inside a fenced block, and a fenced label | Only real headings create paths; no empty intermediate Property is invented; fence labels, indentation, and line breaks remain intact. |
| Two normalized-equal sibling headings, plus equal names under separate parents | The sibling collision rejects the source; the separate parent paths remain distinct and are not merged. |
