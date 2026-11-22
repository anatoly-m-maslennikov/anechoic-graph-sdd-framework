---
atom_id: CA-R-2566
ref_id: CA-R-2566
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Node
tier: 3
status: Active
version: 2
updated_at: 2026-11-02 00:18:22 +0400
carrier_destination:
  file:
    name: CA-R-2566-CORE_META_MODEL-RULE--filter-instances-and-select-maximum-values.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
---
## Summary

Filter instances and select maximum values

## Claim

### Prose Claim


- Select matching instances of the declared kind and its narrower kinds from an explicit Project snapshot.
- Evaluate predicates on each candidate, with Python's short-circuit rules. Resolve references to their target identity. An evaluated predicate with a missing, invalid or unresolved value raises an error.
- Each matching instance contributes one valid scalar. Return the greatest scalar under the applicable Format. Compare datetimes by instant.
- Reject empty, incomplete or incompatible input. Selection and comparison are read-only.
