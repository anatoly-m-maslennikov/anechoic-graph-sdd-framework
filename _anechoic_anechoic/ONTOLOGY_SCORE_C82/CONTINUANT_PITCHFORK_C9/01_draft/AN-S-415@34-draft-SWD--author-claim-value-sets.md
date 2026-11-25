---
atom_family: SPEC
atom_id: AN-S-415
container:
  component: C9
tier: 4
context:
  lens: SWD
state:
  status: draft
  version: 34
  updated_at: 2026-11-05 16:33:24 +0400
---
## Summary

Author Claim Value Sets

## Claim

### Prose Claim


Claim Value Set authoring.


**to** author one Claim Value Set, the Author **must**:

1. identify **`=1`** Property X within **`=1`** Claim;
2. write its finite allowed-value set as `X := A | B | C`;
3. include **`>=1`** unique canonical values **and** treat their order as non-authoritative;
4. retain the complete set as **`=1`** Claim **only** **if** **all** values **must** be accepted, replaced, **and** retired together;
5. interpret `:=` as HAS_ALLOWED_VALUE and `|` as alternatives in that Claim; retain `:=` for allowed-value qualification in a Subject Expression. Neither use assigns an instance value.
