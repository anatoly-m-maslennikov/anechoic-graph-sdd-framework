---
atom_family: SPEC
atom_id: AN-S-1822
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: "archived"
  version: 27
  updated_at: "2026-11-25T22:00:43.995355+00:00"
---
## Summary

Serialize Atom replacement event references

## Claim

### Prose Claim


actual Atom replacement references supplied to the Main Content of a Journal Carrier.


the Main Content of a Journal Carrier **must** preserve the actually supplied predecessor **and** successor Atom references of a replacement observation, including `predecessor_atom_id` **and** `successor_atom_ids` **when** supplied.

- preserve reference values **and** array order as data through safe encoding. array order does **not** establish priority **or** execution order.
- do **not** look up an earlier Journal Event Record, require a predecessor chain, compute a digest, validate the replacement **or** fabricate a baseline **to** append these observations.
- absence of replacement references does **not** establish whether the action was a replacement. do **not** infer missing identities, successors **or** historical facts.
- existing encoded Event Record representations remain readable **without** rewriting their fields, selected representation **or** observed values. legacy **or** nonconforming values remain observations, **not** certified replacements.
- actual source replacement, exact predecessor history **and** successor correctness remain independently governed by AN-S-1846 and AN-S-1730. Journal Carrier append **or** read grants no source-effect permission **and** proves none of those conditions.
