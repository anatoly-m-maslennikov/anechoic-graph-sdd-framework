---
atom_family: PROJECT_CONFIG
atom_id: AN-P-14
structure:
  container:
    component: C9
context:
  template: action
state:
  status: archived
  version: 18
  updated_at: 2026-10-25 01:04:58 +0400
---
## Summary

Resolve and activate Operator priorities

# Summary

Resolve and activate Operator priorities

## Operation

Resolve Operator Priorities **means** the Action that turns applicable Operator input into the effective priority model for an identified Scope **and** Project stage.

### execution

1. identify the affected Scope **and** Project stage from the Operator input **and** its applicable context.
2. resolve the Operator-selected model, effective parameters, active criteria, applicable authority, **and** non-negotiable constraints. retain **every** applicable criterion **without** imposing a fixed catalog **or** comparison by priority order on another model.
3. check whether the input determines an admissible model **and** the parameters needed **to** apply it.
4. **if** that resolution succeeds, activate the resolved priorities **in** the ANECHOIC Framework Instance for the identified context **and** return them as the Action result.

### unresolved input

**if** the selected model, required parameters, authority, **or** context remains unresolved:

- present the known input **and** the exact unresolved point **to** the Operator.
- do **not** invent a model, infer a missing preference, **or** activate an unresolved change.
- report the Action as unresolved, **not** successfully completed.

## Details
