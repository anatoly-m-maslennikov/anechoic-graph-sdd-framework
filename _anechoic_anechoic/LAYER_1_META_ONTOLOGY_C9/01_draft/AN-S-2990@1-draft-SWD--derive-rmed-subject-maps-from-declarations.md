---
atom_family: SPEC
atom_id: AN-S-2990
container:
  component: C9
tier: 3
context:
  lens: SWD
state:
  status: draft
  version: 1
  updated_at: 2026-11-03 14:19:59 +0400
---
## Summary

Derive RMED Subject Maps from Declarations

## Claim

### Prose Claim


- Select and pin Current source Atoms, resolve each active Subject's declared Properties and Relation constraints, then resolve NARROWER inheritance to obtain effective Properties and constraints.
- Label every output Property or constraint as `direct` with its declaring Atom ID@Version or `inherited` with its original Declaration Atom ID@Version.
- Read cardinality, Format, nested names, recursive structure, Relation cardinalities, and a full CFEL Formal Claim only from the applicable Declaration for a displayed Primary Subject or displayed direct or inherited Property.
- Copy each applicable full CFEL Formal Claim block verbatim, including an unparsed or unsupported block; attach its diagnostic without discarding, shortening, merging, inferring, or overriding the Claim.
- Retain a diagnostic rather than treating a missing Declaration as an empty declaration.
