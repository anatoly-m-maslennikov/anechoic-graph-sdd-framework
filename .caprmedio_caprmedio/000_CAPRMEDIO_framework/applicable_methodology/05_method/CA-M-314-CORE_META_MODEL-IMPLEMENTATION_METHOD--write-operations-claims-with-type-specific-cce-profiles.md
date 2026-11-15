---
atom_id: CA-M-314
ref_id: CA-M-314
container:
  scope_unit: CA-SU-11
role: Method
form: Implementation Method
topics:
  main_subject: CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Operations).Header.Context.Form
  dependencies:
  - CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Operations)
  - CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form
    := Action)
  - CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form
    := Workflow)
  - CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form
    := Workflow) >{1+} Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form
    := Step)
  - CAPRMEDIO_STRUCTURE <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Controlled
    English
  - CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role:=Operations)/Workflow
tier: 6
relations:
  child_of:
  - CA-M-307
status: Active
version: 27
updated_at: 2026-11-11 14:09:10 +0400
carrier_destination:
  file:
    name: CA-M-314-CORE_META_MODEL-IMPLEMENTATION_METHOD--write-operations-claims-with-type-specific-cce-profiles.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/05_method
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/05_method/CA-M-314-CORE_META_MODEL-IMPLEMENTATION_METHOD--write-operations-claims-with-type-specific-cce-profiles.md
  source_atom_id: CA-M-314
  source_atom_revision: 27
  source_sha256: 6f38fbd92cc0fe46e32edaa4027e36cdd862dc48c1aeb417ce3307f570cebcbd
  original_relations_sha256: 1037ec3e9bee824bbe0013d533c233bc31238f593358d3400af78e5150b7d7f4
---

## Summary

Write Operations Claims with Type-specific CCE Profiles

## Claim

### Prose Claim

Operations Claims written with Action, Workflow, and Step CCE Profiles when their primary Form is Action, Workflow, or Step.

**to** write an Operations Claim whose primary Form is Action, Workflow, or Step, the Author **must** first resolve that Form **and** then apply **`=1`** primary Form profile:

1. for Action, use **means** to define the named reusable operational behavior. state its required inputs, preconditions, operational contribution, returned results, observable effects, **and** failure results. modality, condition, temporal, quantification, logical, restriction, predicate, **and** comparison Operators **may** constrain that behavior.
2. for Workflow, use **means** to define the reusable graph through Step references, entry, typed transitions, result conditions, **and** terminal outcomes. use condition, temporal, logical, restriction, predicate, **and** comparison Operators **only** with explicit transition scope under CA-M-305-CORE_META_MODEL-METHOD--write-workflow-schemes-using-step-references.
3. for Step, define the invocation binding of **`=1`** referenced Action or Workflow with its parameters **and** inputs. Reference the called definition without copying its behavior.

For an Operations Scope Delegation, Solution, Direct Policy, Approach Policy, or Decision whose actual primary contribution matches Operations semantics, write the Claim under that Form's admitted semantics. Do **not** apply an Action, Workflow, or Step profile merely because the Role is Operations. Those Forms create no executable binding.

## Details

an Operations Claim whose primary Form is Action, Workflow, or Step **must not** combine more than one primary Form profile. subordinate inputs, conditions, results, failures, transitions, **and** effects remain part of the selected Form's single operational contribution.
