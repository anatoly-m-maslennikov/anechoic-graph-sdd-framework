---
atom_family: SPEC
atom_id: AN-S-2605
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: '2026-11-12T12:28:45.296398+00:00'
---
## Summary

Specify Python relation declarations

## Claim

### Prose Claim

- Declare the canonical Relation name, endpoint domains, and any written aliases with `declare_relation`.
- Declare an inverse alias against its canonical Relation. Its source and target slots swap, including their cardinality bounds. Expose the reverse link as a Derived Relation from the same fact.
- Give each endpoint a Model or instance level where the Relation permits that level. An Entity's Model and instance permissions resolve separately.
- Declare direction-specific permissions and apply the appropriate source and target bounds. Unlisted Relations are forbidden where the Entity declares a closed whitelist.
- Declare the inheritable contracts on `NARROWER_THAN`. Python class bases establish the narrowing path. Resolve schema rules through the class MRO and explicit MODEL overrides.

- A canonical Relation declaration has Direct classification by default.
- Endpoint address forms identify canonical Relations, inverse alias addresses, base Atom IDs, and exact represented-content versions. Resolve inverse alias addresses through canonical Relation metadata.
