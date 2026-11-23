---
atom_family: SPEC
atom_id: AN-S-1723
container:
  component: C00
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 11
  updated_at: 2026-10-24 00:51:05 +0400
---
## Summary

Evaluate Requirement checkability

# Evaluate Requirement checkability

**when** an accepted Requirement is used **to** govern work **or** evaluate a result, its checkability Evaluation **must** return `pass` **if** the available evidence identifies **all** of the following:

- recoverable inputs for checking the Requirement;
- a recoverable check procedure;
- a recoverable interpretation that yields **=1** result **in** (`pass`, `fail`).

**if** **any** of these conditions is missing, the checkability Evaluation **must** return `fail`. satisfying them does **not** require a separate Evaluation Atom **unless** applicable authority requires that Atom for the particular case under ANECHOIC-META-REQU-124; an independently governed Evaluation Claim still follows the Atom boundary rules.
