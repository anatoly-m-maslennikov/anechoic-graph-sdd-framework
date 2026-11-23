---
atom_family: SPEC
atom_id: AN-S-2773
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 24
  updated_at: 2026-11-02 08:06:47 +0400
---
## Summary

Serialize explicit Plan blocking

## Claim

### Prose Claim


explicit `A BLOCKS B` facts, including their storage on Plan `A` under `relations.blocks` for Plan `B`.


**every** explicit `A BLOCKS B` fact **must** be stored once on Plan `A` under `relations.blocks`, as a unique canonical Atom ID for Plan `B`; an omitted list encodes **`=0`** outgoing blocking Relations.

- do **not** store a separate inverse list.
- do **not** encode Plan scheduling with `relations.depends_on` **or** `subjects.depends_on`.
- store Plan containment separately on the child under `IS_CONTAINED_BY`, with `CONTAINS` derived; do **not** derive blocking from containment **or** directory order.
