---
atom_id: CA-R-1505
ref_id: CA-R-1505
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Evaluation)
  dependencies:
  - ANECHOIC_MODEL <+ Package/Project Package
  - ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Quality <+ Traceability
  - ANECHOIC_MODEL <+ Event Record
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Evaluation)
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Operations)
tier: 1
status: Active
version: 28
updated_at: 2026-11-10 14:38:45 +0400
carrier_destination:
  file:
    name: CA-R-1505-CORE_META_MODEL-RULE--keep-evaluation-realization-chains-distinct.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1505-CORE_META_MODEL-RULE--keep-evaluation-realization-chains-distinct.md
  source_atom_id: CA-R-1505
  source_atom_revision: 28
  source_sha256: 7e4beb4cb2c27a70388941ef26b7054f08c632c6fa43a122abaa6e4ff6ea10f3
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Keep Evaluation realization chains distinct

## Claim

### Prose Claim


Evaluation realization chains and their associated implementation, evidence, and operational contributions.


an Evaluation Atom's realization chains **must** remain distinct between deterministic test implementations **and** qualitative, probabilistic, statistical, rubric-based, **or** model-judged evaluation implementations.

**every** chain **must** keep these contributions distinguishable:

- its executable Implementation;
- its configuration **or** rubric;
- its factual execution result;
- its Evidence;
- its Verification judgment.

## Details

a shared runner, prompt, judge, report, **or** gate **must not** merge the chains' meanings, results, **or** coverage. the source authority, executable mechanisms, factual Journal Records, **and** reusable Operations definitions retain their distinct roles under CA-R-1683-CORE_META_MODEL-CORE-REQUIREMENT--authority-evaluation-and-operations-remain-distinct **and** CA-R-1684-CORE_META_MODEL-CORE-REQUIREMENT--separate-analysis-from-factual-execution-records.
