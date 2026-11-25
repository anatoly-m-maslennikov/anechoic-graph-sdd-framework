---
atom_family: SPEC
atom_id: AN-S-2605
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-14T07:29:18.360406+00:00'
---
## Summary

Specify Python relation declarations

## Claim

### Prose Claim

- Use `declare_relation` to specify the canonical name, the eligible Model kinds and levels at each endpoint, and any aliases. A matching endpoint pair admits the direct Relation.
- Use `endpoint_pairs` when each source domain admits a specific target domain. Give each pair a `source_endpoint` and a `target_endpoint`. The inverse reverses each pair.
- Declare an inverse alias against its canonical Relation. Its source and target slots swap. An explicitly admitted reverse view derives from the direct fact.
- Specify each endpoint's Model or instance level. Put cardinality and other conditions in the relevant Entity Declarations. Apply those constraints within the Relation's endpoint domain.
- Declare the inheritable contracts on `IS_NARROWER_THAN`. Python class bases establish the narrowing path. Resolve schema rules through the class MRO and explicit MODEL overrides.

- A canonical Relation declaration has Direct classification by default.
- Endpoint address forms identify canonical Relations, inverse alias addresses, base Atom IDs, and exact represented-content versions. Resolve inverse alias addresses through canonical Relation metadata.
