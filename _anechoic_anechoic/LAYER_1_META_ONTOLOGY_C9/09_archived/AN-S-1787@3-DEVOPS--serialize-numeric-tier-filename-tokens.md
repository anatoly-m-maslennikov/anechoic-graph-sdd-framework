---
atom_family: SPEC
atom_id: AN-S-1787
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 3
  updated_at: 2026-10-24 01:50:12 +0400
---
## Summary

Serialize Numeric Tier Filename Tokens

# Summary

Serialize Numeric Tier Filename Tokens

## Scope

Atom filename grammar that represents an Atom's numeric Tier.

## Claim

an Atom filename **must** serialize the Atom's internally carried numeric Tier only through the currently registered filename grammar. Numeric Tier tokens are representations only; a higher integer Tier requires an explicitly registered token rule and **must not** be guessed from a retired Local Tier or Global Tier label. Filename interpretation **must** preserve the Atom identity, owner, target, Scope, and sequence grammar, and a filename alone **must not** become the source of the numeric Tier.

The external Project Goal grammar **must** be recognized before applying any ordinary filename default. No Content Role or Type-to-Tier restriction is introduced by this delivery rule.

## Details
