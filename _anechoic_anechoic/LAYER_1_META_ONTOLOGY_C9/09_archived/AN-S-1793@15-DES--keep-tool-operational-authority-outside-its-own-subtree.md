---
atom_family: SPEC
atom_id: AN-S-1793
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 15
  updated_at: 2026-10-27 19:59:56 +0400
---
## Summary

Keep Tool operational authority outside its own subtree

# Summary

Keep Tool operational authority outside its own subtree

## Scope

Tools' implementation references to methodology Action and Workflow definitions in the anechoic Project.

## Claim

**in** the anechoic Project, a Tool's implementation reference **to** a methodology Action **or** Workflow definition **must not** target an O Atom owned by the Tool's Scope Unit **or** **any** descendant of that Scope Unit.

## Details

- the restriction concerns the owner of the operational definition, **not** the location of the Tool's code, prompts, **or** runtime results.
- methodology Evaluations of their own Action **and** Workflow definitions under CA-R-1518 are **not** Tool implementation references **and** are **not** prohibited by this rule.

this restriction prevents self-reference through the Tool's own subtree; it does **not** establish that **all** indirect dependency cycles are absent.
