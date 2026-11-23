---
atom_family: SPEC
atom_id: AN-S-1719
container:
  component: C9
tier: 7
context:
  lens: QA
state:
  status: archived
  version: 36
  updated_at: 2026-10-29 07:45:29 +0400
---
## Summary

Validate a Demand Atom

## Claim scope

Demand Atoms and their Consumer-owned Producer-result constraints.

## Claim

a Demand is owned by its Consumer **and** constrains **only** one Producer result authorized by the Consumer's accepted Goal.

### Test case

create valid Demand Atoms with Consumer **and** Producer Scope Unit references **in** permitted branches **and** with a later ordered sibling as Consumer **and** an earlier ordered sibling as Producer. **then** remove the Goal-authorized need for the Producer result, change ownership, target an ancestor, direct child, deeper descendant, **or** later ordered sibling, use equal Producer **and** Consumer Local Order, target two results, constrain Producer authority outside the selected result, fully define Producer Scope, **and** add a separate Demand-direction relation Kind.

### Acceptance criteria

**only** fixtures with Consumer ownership, a permitted direction, one exact Goal-authorized need for the Producer result, one exact Implementation result, **and** no additional direction relation pass.

### Failure disposition

record a Concern naming the invalid Demand fact.

## Details
