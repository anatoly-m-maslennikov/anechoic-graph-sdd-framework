---
atom_family: SPEC
atom_id: AN-S-1629
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: active
  version: 23
  updated_at: 2026-11-07 15:18:44 +0400
---

## Summary

Admit the Operations Atom Types

## Claim

### Prose Claim

internal Form values of Operations Atoms.

the admitted Form values of `Atom/(.Header.Role := Operations).Header.Form` **must** include (Action, Workflow, Step, Scope Delegation, Solution, Direct Policy, Approach Policy, Decision). An Operations Atom may use Scope Delegation, Solution, Direct Policy, Approach Policy, or Decision only when its Claim's actual primary contribution matches the reviewed Operations semantics. Those Forms do not create an Action, Workflow, or Step binding.

## Details

Action, Workflow, and Step retain their existing Form admission and behavior. Branch and Fork remain not admitted internal Form values. Linear and Conditional remain Step forms carried by Step definitions, not additional Operations Atom Forms.
