---
atom_family: SPEC
atom_id: AN-S-4415
container:
  component: C24
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 1
  updated_at: 2026-11-10 11:53:32 +0400
---
## Summary

Keep review completion separate from applied edits

## Claim scope

completion results produced by the RMED review prompt Implementation for a selected Atom **or** selection.

## Claim

### Prose Claim

the Implementation **must** report completion **only** from complete initial check coverage **and** resolved findings, rather than from the existence of a report **or** an applied edit.

## Details

- an initial failed check is a completed check with a finding; a blocked **or** unperformed check is incomplete coverage.
- confirmed findings are resolved by an authorized correction **or** a recorded rejection supported by the supplied rules. partial correction does **not** resolve remaining findings **or** coverage.
- **every** finding retains its own disposition. a nonempty correction list **or** an empty unresolved list alone does **not** establish that **all** findings were handled. a correction-permission blocker does **not** turn a concluded initial check into an unperformed check.
- a completed selection requires completion evidence for **every** selected Atom. independent completed Atoms remain distinguishable from the unfinished selection.
- completion after fixes records completion of the admitted one-pass work, **not** a claim that saved output passed another Evaluation. this specification adds no recheck Step.
