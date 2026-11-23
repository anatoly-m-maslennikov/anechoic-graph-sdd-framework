---
atom_family: SPEC
atom_id: AN-S-2716
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 8
  updated_at: '2026-11-12T20:24:10.208771+00:00'
---
## Summary

Define HAS_INVERSE

## Claim

### Prose Claim

HAS_INVERSE binds a direct graph Relation to its derived inverse graph Relation. The Host is Direct and the Target is Derived. The inverse swaps Host and Target for each admitted direct fact. The two Relation identities remain distinct. The direct Declaration owns the shared meaning, endpoint signature, endpoint conditions and this binding; the derived Declaration supplies the reverse written counterpart binding and its own lexical alias when one exists. A bound inverse is inferred from the direct fact and is not authored separately. The inferred IS_DERIVED_RELATION_OF metadata is not repeated in the minimal derived Declaration. A qualified derived counterpart requires its qualification at the direct Declaration and is not an unconditional inverse.

`<-->` is the Subject notation alias for this binding. Written as `Relation//DIRECT <--> Relation//DERIVED` inside the direct Declaration, its left operand identifies the direct Relation and its right operand identifies the derived inverse. It is neither equality nor aliasing of the two Relation identities. The binding does not grant endpoint permissions or outgoing cardinalities.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='HAS_INVERSE',
    source_endpoint={'level': 'instances', 'entity_paths': ('Relation',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Relation',)},
    written_alias='<-->',
)
```

