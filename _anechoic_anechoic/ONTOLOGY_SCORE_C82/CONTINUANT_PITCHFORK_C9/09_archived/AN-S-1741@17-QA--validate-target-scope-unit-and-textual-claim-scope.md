---
atom_family: SPEC
atom_id: AN-S-1741
container:
  component: C9
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 17
  updated_at: 2026-10-24 19:39:48 +0400
---
## Summary

Validate Target Scope Unit **and** textual Claim Scope

# Summary

Validate Target Scope Unit **and** textual Claim Scope

## Scope

the distinction between an Atom's Claim Target Scope Unit **and** its textual applicability.

## Claim

### Claim checked

**every** Atom resolves **`=1`** Claim Target Scope Unit; its Claim Scope remains applicability restrictions **in** the body sections registered by CA-D-495, including Scope for RMED, **not** another structural target **or** frontmatter Property.

## Details

### Test case

create a Current-scope Atom with its own Scope Unit explicitly carried as target **and** a Claim restricted **to** Python files; repeat with a composite restriction. for RMED, carry those restrictions **in** Scope **and** the qualified contribution **in** Claim. create a permitted Demand with a different explicit target, a parent-owned Goal for its direct child, an external Project Goal with its Author's registered Operator name **and** an explicit Project target, **and** a Plan inside nested Hubs. **then** omit the internally required target even **when** filename **or** placement identifies its owner, provide two targets, use a Hub as a target, leave the target unresolved, duplicate textual applicability **in** frontmatter, **or** infer a target **or** ownership change from the textual restriction alone.

### Acceptance criteria

valid targets resolve **to** **`=1`** Scope Unit. authoring defaults select **and** carry the current Scope Unit **where** one exists; reading does **not** repair an omitted target from placement; external Project Goals retain their explicit target. narrower **or** composite applicability alone leaves a Current-scope Atom Current-scope. a different permitted target yields a Relational Atom **without** transferring ownership **or** changing Scope Unit ancestry. Hub nesting does **not** create another target. **every** invalid fixture fails with the exact missing, unresolved, duplicate, misclassified, **or** independently duplicated fact identified.

### Failure disposition

report the affected Atom **and** target, ownership, **or** textual-applicability distinction; preserve the source **until** an authorized correction is selected.
