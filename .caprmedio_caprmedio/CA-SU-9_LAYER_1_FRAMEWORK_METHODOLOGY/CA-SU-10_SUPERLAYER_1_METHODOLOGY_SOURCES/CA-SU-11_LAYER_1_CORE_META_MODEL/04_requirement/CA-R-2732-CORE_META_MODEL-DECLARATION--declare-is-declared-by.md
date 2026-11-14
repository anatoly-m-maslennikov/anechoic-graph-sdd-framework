---
atom_id: CA-R-2732
ref_id: CA-R-2732
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Relation//IS_DECLARED_BY
tier: 1
status: active
version: 4
updated_at: '2026-11-13T22:37:32.288997+00:00'
carrier_destination:
  file:
    name: CA-R-2732-CORE_META_MODEL-DECLARATION--declare-is-declared-by.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
---
## Summary

Declare IS_DECLARED_BY

## Claim

### Prose Claim

IS_DECLARED_BY relates a declared model entity or instance to its canonical declaring Atom, qualified by CA-R-2278. The Target has Header.Role Requirement and Header.Form in (Declaration, Relation Declaration). Derive this view only when that Atom's GOVERNS link identifies the declared Subject and the declaring ownership qualification is satisfied in the selected effective MODEL. An arbitrary GOVERNS link from another role or form does not produce IS_DECLARED_BY.

The Host is the qualified Declaration's governed Subject; it may be outside the Node branch. The Target is the qualified declaring Atom. This view reuses the existing direct GOVERNS fact and adds no independently stored reverse fact. Its direction reverses the selected, qualified GOVERNS fact; it is not an unconditional HAS_INVERSE binding for GOVERNS.

Forward `Host ((IS_DECLARED_BY)) Target` and reverse `Target <((IS_DECLARED_BY)) Host` are written views of that same derived fact. CA-R-1199 retains the general GOVERNS meaning. CA-R-2278 supplies the declaring ownership qualification; this Declaration retains the qualified endpoint transformation. Neither a derivation reference nor a displayed view grants permission or cardinality.
### Formal Claim

```python
from caprmedio.formal_claims import declare_relation

declare_relation(
    relation_name='IS_DECLARED_BY',
    derived_from='GOVERNS',
    source_endpoint={'level': 'model_entities_or_instances'},
    target_endpoint={'level': 'instances', 'entity_paths': ('Atom/(.Header.Context.Role:=Requirement)/(.Header.Context.Form in (Declaration, Relation Declaration))',)},
)
```

