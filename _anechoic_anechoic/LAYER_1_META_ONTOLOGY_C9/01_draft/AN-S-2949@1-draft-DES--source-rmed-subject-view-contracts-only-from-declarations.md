---
atom_family: SPEC
atom_id: AN-S-2949
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: draft
  version: 1
  updated_at: 2026-11-03 14:19:59 +0400
---
## Summary

Source RMED Subject View Contracts Only from Declarations

## Claim

### Prose Claim


For a selected effective MODEL, an RMED Subject Map must obtain a displayed Primary Subject's or displayed direct or inherited Property's allowed Relation cardinalities, Property presence, direct-value cardinality, direct-value Format, nested Property names, recursive Property structure, and full CFEL Formal Claim only from its effective Current Atom/(.Header.Role := Requirement)/(.Header.Form := Declaration). It must preserve each applicable Declaration's full CFEL Formal Claim block verbatim; a missing, unsupported, or conflicting Declaration result is a diagnostic, not a fallback to another RMED Atom.

An inherited Property must cite and reuse its original effective Declaration; the Map must not create a local Property node or a replacement Declaration. No Claim merger, override inference, or inferred cardinality, Format, nested name, recursive structure, or Formal Claim is permitted.

Absence is distinct from an empty declared value: an empty value is shown only when the selected Declaration explicitly carries it; missing or unsupported CFEL remains unresolved.
