---
atom_family: SPEC
atom_id: AN-S-3710
container:
  component: C20
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 7
  updated_at: 2026-10-24 11:58:20 +0400
---
## Summary

Pause on incomplete Base Revise coverage

# Summary

Pause on incomplete Base Revise coverage

## Scope

RMED Atoms Base Revise execution in WORKFLOW_ORCHESTRATOR.

## Claim

every Base Revise main phase **must** pass a Coverage Gate **before** continuation **or** completed status.

## Details

- gather covers the explicitly frozen selection **and** rules, **not** an inferred full Project corpus.
- check covers **all** **`=6`** checks for **all** selected Atoms; failed checks can be concluded, blocked checks cannot.
- fix covers every selected Atom **and** every recorded finding disposition, **not** a post-fix semantic pass.
- coverage below **`=100`** percent **or** unknown coverage pauses **and** exposes an Operator question with missing work. a client-side observer presents this question; an idle worker does **not** invent a chat notification.
