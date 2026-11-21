---
atom_family: TKT
atom_id: AN-T-1486
container:
  atom: AN-T-1487
priority: 2
context:
  template: task
state:
  status: done
  version: 3
  updated_at: 2026-11-07 18:02:00 +0400
---

## Summary

Define Implementation Atoms

## Objective

Define and adopt I / Code Synopsis for describing actual implementation, including legacy code with incomplete or absent specifications.

## Settled inputs

- RMEDO describes the required state. I describes the actual implementation.
- The chosen Form name is Code Synopsis: I / Code Synopsis.
- I / Code Synopsis is allowed by default in every Scope Unit, within its Subject boundaries.
- I can describe code parts, behavior, structure and rationale.
- An implementation description requires no specification.
- A difference from a specification is a neutral observation. It becomes a Concern when it is assessed as a matter requiring resolution.
- P covers work and its execution reports. A provides analysis informing specifications and tasks. C records matters to resolve.

## Work

1. Define the I Role and Code Synopsis Form, including content and code-reference contracts.
2. Distinguish implementation descriptions, rationale and observed specification differences. Preserve the distinction between supported facts and inferred explanations.
3. Settle identity, scope, lifecycle and how descriptions follow changes in code.
4. Define links to optional specifications and to analysis, Concerns and Tasks when those exist.
5. Create model Drafts; review, repair, promote and check them.
6. Identify affected authoring, reader and projection contracts for their implementation owners.

## Definition of Done

- Reviewed Current model Atoms define I / Code Synopsis and its boundaries with RMEDO, P, A and C.
- Identity, code references and lifecycle are declared.
- Examples cover legacy code without a specification and a neutral difference from an existing specification.
- Source checks and required consumer handoffs are recorded separately from runtime verification.
