---
atom_family: SPEC
atom_id: AN-S-2724
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: active
  version: 4
  updated_at: '2026-11-13T22:37:32.288997+00:00'
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
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='IS_DECLARED_BY',
    derived_from='GOVERNS',
    source_endpoint={'level': 'model_entities_or_instances'},
    target_endpoint={'level': 'instances', 'entity_paths': ('Atom/(.Header.Context.Role:=Requirement)/(.Header.Context.Form in (Declaration, Relation Declaration))',)},
)
```

