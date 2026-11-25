---
atom_family: SPEC
atom_id: AN-S-1748
container:
  component: C58
tier: 3
context:
  lens: DOM/MTD
state:
  status: active
  version: 15
  updated_at: '2026-11-25T21:19:17.763117+00:00'
---
## Summary
Validate Atom Content Role classification

## Claim

### Prose Claim

For a native Atom, check that its authored contribution fits the declared Family and applicable Template under AN-S-2301. Report the relevant content, governing declaration, and result. Keep unresolved evidence visible.

Use the following comparison only when reviewing a legacy Content Role carrier.

the classification Evaluation **must** fail **if** an Atom's Content Role does **not** match its actual contribution under the Specification **and** Change definitions.

- use the evaluated Atom's declared Content Role, complete Main Content, **and** applicable Specification **and** Change definitions as the input evidence.
- compare the declared Content Role with the contribution expressed **in** that Main Content, using the following classification table.
- report unresolved **when** required evidence is unavailable, unresolved, **or** contradictory; **otherwise**, report pass **if** the declared Content Role matches the observed contribution **and** fail **if** it does **not**.
- identify the evaluated Atom **and** report the declared Content Role, relevant content excerpt, applicable definition, **and** comparison result.

| Claim contribution | Expected classification |
|---|---|
| a model definition, required property, permission, **or** Actor participation/authorization policy governing a Concern, Analysis & Advisory, Task, Action, **or** Workflow | Requirement |
| a convention for authoring **or** constructing that content | Method |
| a falsifiable correctness check | Evaluation |
| a Carrier's fields, format, **or** placement | Delivery |
| a particular unresolved issue, analytical finding, **or** intended Task | the matching Concern, Analysis & Advisory, **or** Plan role |
| a particular reusable Action behavior, Workflow graph, **or** Step invocation binding | Operations |


reusing the specified content's role as the specification's role **must** fail this check. a long-lived Concern **or** reusable Workflow **must not** fail merely because its lifetime is long.
