---
atom_family: SPEC
atom_id: AN-S-3406
container:
  component: C9
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 6
  updated_at: 2026-09-28 06:30:40 +0400
---
## Summary

Check Updated At preservation during formatting changes

# Check Updated At preservation during formatting changes

the Evaluation **must** fail **if** **any** of these conditions is observed:

- a formatting-only change changes the Atom's Updated At value.
- a lossless Subject serialization migration changes Updated At despite preserving the canonical targets **and** Relation meanings.
- a changed Claim, Summary, applicability, Content Role, Type, Subject target, **or** authored Relation meaning is accepted as a formatting-only change.
- timestamp preservation is treated as permission **to** omit a required Version increment **or** discard the exact prior Carrier.

valid cases include whitespace **or** markup normalization **and** lossless conversion from temporal Subject nesting **to** flat direct references. compare their **before** **and** **after** Claim content, interpreted Property values, references, **and** Relation meanings; require the same Updated At value **and** apply the independent Revision rules. an ambiguous change does **not** establish a passing formatting-only case.
