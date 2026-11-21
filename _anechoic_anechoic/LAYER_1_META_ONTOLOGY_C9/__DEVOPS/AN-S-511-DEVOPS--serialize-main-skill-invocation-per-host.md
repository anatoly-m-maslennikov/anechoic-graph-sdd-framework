---
atom_family: SPEC
atom_id: AN-S-511
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: active
  version: 23
  updated_at: 2026-11-02 18:35:20 +0400
---
## Summary

Serialize Main Skill Invocation per Host

## Claim

### Prose Claim


Host Invocations for the ANECHOIC Main Skill **and** separately authorized compatibility layers.


for the ANECHOIC Main Skill, the Host Invocation **must** serialize as `$ca` **in** Codex; **if** a Claude compatibility Extension **or** Operator-provided compatibility layer is separately authorized by the Operator, **then** its Host Invocation **must** serialize as `/ca` **in** Claude.
