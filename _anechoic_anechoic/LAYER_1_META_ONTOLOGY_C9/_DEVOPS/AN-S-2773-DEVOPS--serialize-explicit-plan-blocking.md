---
atom_family: SPEC
atom_id: AN-S-2773
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: active
  version: 26
  updated_at: 2026-11-04 16:52:59 +0400
---
## Summary

Serialize explicit Plan blocking

## Claim

### Prose Claim

For each direct `B IS_BLOCKED_BY A` fact, encode the prerequisite Plan `A` once as a canonical Atom ID in the dependent Plan `B` under `relations.IS_BLOCKED_BY`. Use a YAML sequence of unique Plan Atom IDs; an omitted list encodes no outgoing blocking Relations. Resolve each referenced ID to its intended Plan under applicable authority.

Do not store the derived `A BLOCKS B` view as a second fact. Do not encode Plan scheduling with `relations.depends_on` or `subjects.depends_on`. Store Plan containment separately under `IS_CONTAINED_BY`; do not derive blocking from containment or directory order.
