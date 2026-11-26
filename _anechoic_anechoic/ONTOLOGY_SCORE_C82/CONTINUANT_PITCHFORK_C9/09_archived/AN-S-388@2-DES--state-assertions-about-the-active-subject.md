---
atom_family: SPEC
atom_id: AN-S-388
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-25T22:54:43.211128+00:00"
---
## Summary

State assertions about the active Subject

## Claim

### Prose Claim


- For an Atom with an active Subject, all assertions and prescriptions concern that active Subject.
- References to other Subjects describe the active Subject's endpoints, inputs, outputs, conditions or dependencies.
- Independent assertions about another Subject belong in an Atom with that active Subject.
- For an Atom whose active Subject is a Node, each Relation count constrains that active Subject's own outgoing Relations.
