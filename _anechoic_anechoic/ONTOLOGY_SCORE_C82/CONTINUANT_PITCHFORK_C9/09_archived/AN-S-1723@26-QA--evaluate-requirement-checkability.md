---
atom_family: SPEC
atom_id: AN-S-1723
container:
  component: C9
tier: 3
context:
  lens: QA
state:
  status: "archived"
  version: 26
  updated_at: "2026-11-25T20:57:08.964617+00:00"
---
## Summary

Evaluate Requirement checkability

## Claim

### Prose Claim


**when** an accepted Requirement is used **to** govern work **or** evaluate a result, its checkability Evaluation **must** return `pass` **if** the available evidence identifies **all** of the following:

- recoverable inputs for checking the Requirement;
- a recoverable check procedure;
- a recoverable interpretation that yields **=1** result **in** (`pass`, `fail`).

**if** **any** of these conditions is missing, the checkability Evaluation **must** return `fail`. satisfying them does **not** require a separate Evaluation Atom **unless** applicable authority requires that Atom for the particular case under CA-R-1707; an independently governed Evaluation Claim still follows the Atom boundary rules.
