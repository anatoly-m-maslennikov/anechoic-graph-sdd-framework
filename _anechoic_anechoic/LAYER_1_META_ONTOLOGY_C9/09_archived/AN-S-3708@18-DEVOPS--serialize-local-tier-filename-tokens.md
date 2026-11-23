---
atom_family: SPEC
atom_id: AN-S-3708
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 18
  updated_at: 2026-10-23 03:14:50 +0400
---
## Summary

Serialize Local Tier Filename Tokens

# Summary

Serialize Local Tier Filename Tokens

## Scope

Ordinary Atom filenames subject **to** the role-tier restrictions under CA-R-1566.

## Claim

an ordinary Atom filename **must** serialize Principle as `PRINCIPLE`, Core as `CORE`, General as `GENERAL`, **and** the default Standard Local Tier by omitting the Local Tier segment at the registered descriptor position **after** its identity **and** current Scope owner. `PRINCIPLE` is admitted **only** for a Project-scoped Atom; `STD`, `STANDARD`, `DETAIL`, **and** combined tier segments **must not** be serialized. the external Project Goal's registered tierless grammar **must** be recognized **before** applying the ordinary omitted-Standard default; a tier token **must not** replace **or** alter the registered identity, owner, target, **or** sequence grammar of a Goal **or** Plan.

## Details
