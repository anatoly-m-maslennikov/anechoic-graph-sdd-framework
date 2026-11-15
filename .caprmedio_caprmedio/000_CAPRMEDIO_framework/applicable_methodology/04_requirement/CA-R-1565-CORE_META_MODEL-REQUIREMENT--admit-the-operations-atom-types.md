---
atom_id: CA-R-1565
ref_id: CA-R-1565
container:
  scope_unit: CA-SU-11
role: Requirement
form: Requirement
topics:
  main_subject: CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Operations).Header.Context.Form
  dependencies:
  - CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Operations)
  - CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form := Action)
  - CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form := Workflow)
  - CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form := Workflow) >{1+} Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form := Step)
tier: 1
status: Active
version: 23
updated_at: "2026-11-07 15:18:44 +0400"
carrier_destination:
  file:
    name: CA-R-1565-CORE_META_MODEL-REQUIREMENT--admit-the-operations-atom-types.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1565-CORE_META_MODEL-REQUIREMENT--admit-the-operations-atom-types.md
  source_atom_id: CA-R-1565
  source_atom_revision: 23
  source_sha256: de179109b64fdb8d22be31169371b28dd2e7c7fd643c87858e08ff62a7ee67f8
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Admit the Operations Atom Types

## Claim

### Prose Claim

internal Form values of Operations Atoms.

the admitted Form values of `Atom/(.Header.Role := Operations).Header.Form` **must** include (Action, Workflow, Step, Scope Delegation, Solution, Direct Policy, Approach Policy, Decision). An Operations Atom may use Scope Delegation, Solution, Direct Policy, Approach Policy, or Decision only when its Claim's actual primary contribution matches the reviewed Operations semantics. Those Forms do not create an Action, Workflow, or Step binding.

## Details

Action, Workflow, and Step retain their existing Form admission and behavior. Branch and Fork remain not admitted internal Form values. Linear and Conditional remain Step forms carried by Step definitions, not additional Operations Atom Forms.
