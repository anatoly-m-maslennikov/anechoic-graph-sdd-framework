---
atom_family: SPEC
atom_id: AN-S-1907
structure:
  container:
    component: C15
  tier: 4
context:
  lens: SWD
state:
  status: active
  version: 15
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Ratchet typing and automation adoption

## Claim



### Prose Claim
advance PROGRAMMATIC typing **and** automation through bounded target selection,
explicit tool configuration, **and** deliberate expansion. Evaluation authority
owns acceptance profiles **and** regression policy under CA-E-539, CA-E-540,
**and** the applicable behavioral Evaluation.

## Details


### Applicable when

apply **when** a Tool, App backend service, **or** MCP component adds **or** materially
changes source that falls within an admitted typing, formatting, linting, **or**
behavioral-check capability.

### Procedure

1. resolve **every** selected typing, formatting, linting, **or** behavioral-check
   capability from its accepted Method owner.
2. read its current tool, version, profile, **and** bounded target materialization
   from canonical configuration **or** Implementation; read carrier placement **and**
   encoding from Delivery.
3. keep formatting, linting, typing, **and** behavioral evidence distinct.
4. provide changed **or** new target evidence **and** its current admitted baseline
   **to** the applicable Evaluation for its regression decision.
5. expand **or** replace a selected capability **only** through a Method change;
   materialize that change separately **and** preserve actual run evidence through its
   declared owner. Journal writes remain limited to the existing business-lifecycle
   contract; technical checks do not add hidden Journal effects.

### Outcome

automation **and** typing improve monotonically at an admitted surface **without**
turning an unselected tool, version, **or** strictness level into shared authority.

### Failure or stop

return unresolved selection **when** no accepted Method owns the tool choice **or**
the bounded materialization is unavailable. Evaluation authority determines
whether the supplied baseline **and** execution evidence admit the claimed ratchet.

### Sources

- [Ruff documentation](https://docs.astral.sh/ruff/)
- [Mypy: using Mypy with an existing codebase](https://mypy.readthedocs.io/en/stable/existing_code.html)
- [CA-A-053 — Reconcile shared PROGRAMMATIC policy decisions](../02_analysis_and_advisory/CA-A-053-PROGRAMMATIC-ANALYSIS_RPRT--reconcile-shared-programmatic-policy-decisions.md)
