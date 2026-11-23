---
atom_id: CA-E-667
ref_id: CA-E-667@4
container:
  scope_unit: CA-SU-00
role: Evaluation
form: Eval Policy
topics:
  main_subject: ANECHOIC_MODEL <+ Project
  dependencies:
  - ANECHOIC_MODEL <+ Project
  - ANECHOIC_MODEL <+ Atom.Header.Tier
  - ANECHOIC_MODEL <+ Atom.Header.Role
  - ANECHOIC_MODEL <+ Entity/Object/Continuant/Actor/Operator
  - ANECHOIC_MODEL <+ Atom.Content
  - ANECHOIC_MODEL <+ Atom/(.Header.Role := Evaluation)
  - ANECHOIC_MODEL <+ Atom
  - ANECHOIC_MODEL <+ Atom/(.Header.Role := Plan)
  - ANECHOIC_MODEL <+ Atom/(.Header.Role := Requirement)
  - ANECHOIC_MODEL <+ Atom/(.Header.Role := Method)
  - ANECHOIC_MODEL <+ Atom/(.Header.Role := Delivery)
  - ANECHOIC_MODEL <+ Atom/(.Header.Role := Operations)
  - ANECHOIC_MODEL <+ Actor
tier: 3
relations:
  child_of:
  - CA-M-447
  - CA-M-446
  - CA-E-001
status: archived
version: 4
updated_at: 2026-11-11 05:09:29 +0400
carrier_destination:
  file:
    name: CA-E-667@4-ANECHOIC-EVAL_POLICY--check-the-project-wide-foundation-and-core-set.md
    path: .anechoic_anechoic/06_evaluation/archive
cce_version: cce_1
cce_form: evaluation
llm_session_ids:
- codex:01a02650-eff7-7453-8c37-0699b36773c6
current_scope_unit: anechoic
---
## Summary

Evaluate the current Principle and Core set

## Claim

### Prose Claim


the Principle **and** Core set Evaluation **must** return `fail` **if** a known Project-wide invariant has no canonical owner, a Principle is **only** a narrow application rather than a broad commitment, a required supporting Core Claim is absent, Claims conflict **or** independently duplicate authority **in** the same context, **or** an Atom has an incompatible Local Tier **or** Content Role; **otherwise**, it **may** return `pass` for the reviewed frontier **without** claiming that undiscovered gaps are impossible. evaluate Principle Content Roles under CA-E-482; the former Actor-policy interpretation of Plan does **not** create an exception **to** current Content Role authority. faithful Core specialization **must not** count as duplicate authority; fixed child counts, a universal RMED checklist per Principle, expansion from Intent, **and** formula/text equivalence **must not** be acceptance conditions. report missing support **and** conflicting owners **to** the Operator **without** silently selecting a winner.
