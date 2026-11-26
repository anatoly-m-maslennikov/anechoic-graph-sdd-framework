---
atom_family: SPEC
atom_id: AN-S-391
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-25T21:02:03.098414+00:00"
---
## Summary

Distinguish event time from record insertion time

## Claim

### Prose Claim


- Event Record.happened_at is the time the recorded event happened.
- Event Record.inserted_at is the time the record was added to its Journal.
- Delayed insertion does not replace happened_at with inserted_at.
