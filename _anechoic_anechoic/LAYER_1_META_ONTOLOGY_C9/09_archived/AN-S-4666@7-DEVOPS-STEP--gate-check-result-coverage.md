---
atom_family: SPEC
atom_id: AN-S-4666
container:
  component: C9
tier: 3
context:
  template: step
  lens: DevOps
state:
  status: archived
  version: 7
  updated_at: 2026-10-23 03:06:32 +0400
---
## Summary

Gate check result coverage

# Summary

Gate check result coverage

## Operation

the check Coverage Gate substep **must** invoke **`=1`** Action, CA-O-118, with stage=check **after** the main check Step **and** **before** continuation.

## Details

- inputs: frozen selection, saved Step results, required coverage obligations **and** shared Run evidence.
- covered permits continuation; ask_operator interrupts with the saved missing-work question.
- retain the existing Run ID **and** Journal; do **not** dispatch another Atom reviewer **or** replay completed effects.
