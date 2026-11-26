---
atom_family: SPEC
atom_id: AN-S-479
container:
  component: C9
tier: 2
context:
  lens: DevOps
state:
  status: "archived"
  version: 33
  updated_at: "2026-11-25T22:07:21.298546+00:00"
---
## Summary

Store every Atom Property in one internal location

## Claim

### Prose Claim


Atom Property representation in an Atom Markdown File Carrier.


Use YAML Frontmatter for an Atom's metadata properties. Use named Markdown
Main Content sections for `content.*` properties. Each applicable Atom Property
has one canonical internal location; its value is not duplicated between YAML
and Markdown.

This reusable Policy governs Atom representation. It does not create a Carrier
or a CARRIES fact for each property or section, and it does not change the
owning direction of an Atom-to-Atom Relation.

Qualified classifications are carried as ordinary metadata properties. For example, `Atom/(.Header.Role := Concern)` selects the Atom's `role` value, and a qualified Form selects its `form` value; neither creates a nested Role object. Use the property names and canonical value encodings registered by the applicable D policy, using AN-S-3160 for native Atoms and AN-S-1039@11 for legacy encoding, rather than inventing a new field from the display path.

## Semantics

YAML and Markdown are carrier locations for different Atom properties, not
alternative authorities for the same value. A section's name identifies its
`content.*` property; a metadata property remains a YAML value.

## Details

This Policy incorporates
the reusable placement boundary supported by CA-D-357 without creating a
per-field representation entity.
