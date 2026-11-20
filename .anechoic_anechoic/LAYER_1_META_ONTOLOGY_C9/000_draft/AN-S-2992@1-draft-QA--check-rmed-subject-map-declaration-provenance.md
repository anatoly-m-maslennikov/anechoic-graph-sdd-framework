---
identity:
  atom_id: AN-S-2992
context:
  container:
    component: C9
  tier: 3
  lens: QA
state:
  status: draft
  version: 1
  updated_at: 2026-11-03 14:19:59 +0400
---
## Summary

Check RMED Subject Map Declaration Provenance

## Claim

### Prose Claim


- Pass when every displayed Primary Subject, direct or inherited Property, or Relation constraint identifies its effective Current Requirement/Form: Declaration by Atom ID@Version, preserves direct versus inherited source labeling, and preserves each applicable full CFEL Formal Claim block verbatim with any parse diagnostic.
- Fail when any cardinality, Format, Property presence, nested name, recursive structure, Relation cardinality, or Formal Claim is taken from a non-Declaration RMED Atom.
- Fail when missing provenance, a fabricated inherited Declaration, missing or conflicting Declaration, or unsupported CFEL is presented as an empty or authoritative result.
- Check one direct Declaration and one inherited Property reusing its original Declaration; check missing provenance, a non-Declaration source, unsupported CFEL, absent Declaration, conflicting Declarations, and a fabricated local inherited Declaration.
