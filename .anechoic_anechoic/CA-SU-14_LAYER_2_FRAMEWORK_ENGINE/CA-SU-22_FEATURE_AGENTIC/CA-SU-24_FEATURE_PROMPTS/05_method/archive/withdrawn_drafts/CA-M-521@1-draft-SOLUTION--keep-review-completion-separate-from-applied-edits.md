---
identity:
  atom_id: CA-M-521
  ref_id: CA-M-521@1-draft
context:
  container:
    scope_unit: CA-SU-24
  role: method
  form: solution
  topics:
    main_subject: ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Quality <+ Traceability
    dependencies:
    - ANECHOIC_MODEL <+ Atom
    - ANECHOIC_MODEL <+ Atom/(.Header.Role := Evaluation)
    - ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Quality <+ Verification <+
      Coverage
    - ANECHOIC_MODEL <+ Term//Property
  tier: 3
state:
  status: draft
  version: 1
  updated_at: 2026-11-10 11:53:32 +0400
destination:
  file:
    name: CA-M-521@1-draft-SOLUTION--keep-review-completion-separate-from-applied-edits.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-22_FEATURE_AGENTIC/CA-SU-24_FEATURE_PROMPTS/05_method/draft
current_scope_unit: PROMPTS
claim_target_scope_unit: PROMPTS
author: Anatoly Maslennikov
relations:
  IS_REPLACEMENT_FOR:
  - CA-R-1802
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
