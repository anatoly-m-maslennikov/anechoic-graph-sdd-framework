---
atom_id: CA-R-2551
ref_id: CA-R-2551
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: CAPRMEDIO_MODEL <+ Node.**
tier: 3
status: Active
version: 2
updated_at: 2026-11-02 00:18:22 +0400
carrier_destination:
  file:
    name: CA-R-2551-CORE_META_MODEL-RULE--require-unique-property-tuples.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2551-CORE_META_MODEL-CFEL--require-unique-property-tuples.md
  source_atom_id: CA-R-2551
  source_atom_revision: 2
  source_sha256: af2df8081681ee02f4099086986490f5f0217561c593a6ca31f1bbae89ce047d
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Require unique Property tuples

## Claim

### Prose Claim

Require distinct value tuples across the selected Project instances. An optional condition restricts the population.

- Use each selected instance's state in one explicit Project snapshot. Use one state per selected logical instance. Without a condition, evaluate the complete selected population regardless of Status Group or containment, including selected Drafts and Archived instances. An incomplete or unresolved population is an error. A known empty population satisfies uniqueness.
- Evaluate a condition on each candidate instance before resolving tuple Properties. Relative Properties bind to that same instance. False excludes it; unresolved, invalid or ambiguous conditions are errors. Use Python Boolean expressions.
- For each selected instance, bind every tuple Property to that same instance. Each must have exactly one valid scalar value; missing, invalid or multiple values fail the constraint.
- Two distinct selected logical instances must not have equal value tuples. Repeated references or Carrier representations of the same logical instance do not create additional instances. Do not infer that two instances are one merely because their key tuples match.
- Compare scalar values in their declared Format without implicit normalization or coercion. A declared reference compares by its resolved target identity; an absent or ambiguous binding is an error, with no raw Carrier-locator fallback. Tuple components need not be individually unique.
- Optional Properties require an explicitly resolved subset whose members carry the required values; do not silently skip missing rows.

Declare the tuple keys and any population restriction with the Python Model.
