---
identity:
  atom_id: AN-S-327
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 27
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Reserve Subject Expression Separators

## Claim

### Prose Claim


Term names in Subject Expressions.


a Term name **must not** contain unescaped `/`, `//`, `.`, `:`, `+>`, `<+`, `>|`, `|<`, `((`, `))`, `(`, `)`, `[`, `]`, `{`, or `}`. These are reserved Subject Expression syntax for specialization or instances, Property and allowed-value qualification, containment, classification, named Relations, logical grouping, direct-value Format, or cardinality. A backslash escapes a literal operator character in a name; this Rule does not ban such escaped literal name characters or invent a quote DSL. This Term-name rule does not make the RHS name after `//` a Term; that operand identifies an instance that already exists or is explicitly introduced by applicable defining authority under its separate naming/source authority. Syntax alone neither creates nor admits the instance. The lowercase `atom` keyword and its selector punctuation remain registered initial-selector syntax under CA-R-1321, not a broadened Term-name policy.
