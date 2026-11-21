---
atom_family: SPEC
atom_id: AN-S-1510
container:
  component: C15
tier: 1
context:
  lens: SWD
state:
  status: active
  version: 14
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Implement only declared business logic

## Claim



### Prose Claim
Implement business logic **only** as declared in the applicable Active RMED. **Do not** invent additional policies, restrictions, approval gates, lifecycle rules or workflows. **When** the specification has a gap or conflict affecting the behavior, ask the Operator **before** implementing that behavior.

## Details

### Scope

New or changed PROGRAMMATIC implementation, including its tests.


1. Read the applicable Active RMED before changing behavior. A derived prompt helps find and use the rules; it does not add authority.
2. Choose ordinary implementation details freely within those rules. A choice of algorithm, function layout or internal data structure does not require its own policy when it preserves the declared behavior and constraints.
3. If an additional business rule seems necessary, explain the gap and the smallest proposed change to the Operator. Do not silently implement it or make tests require it. Continue independent work that does not depend on that decision.
4. After the Operator resolves the gap, align the affected RMED before implementing the new business rule. Do not create a new approval mechanism to enforce this Method.

### Outcome

Implementation and tests realize the declared behavior without adding an implicit second specification.

### Failure or stop

Pause the affected behavior when its business meaning requires an undeclared decision. This Method does not authorize removing existing checks or overriding applicable Active RMED without an Operator decision.
