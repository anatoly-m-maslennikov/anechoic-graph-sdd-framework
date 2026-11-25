---
atom_family: SPEC
atom_id: AN-S-511
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: "archived"
  version: 23
  updated_at: "2026-11-25T21:49:08.200364+00:00"
---
## Summary

Serialize Main Skill Invocation per Host

## Claim

### Prose Claim


Host Invocations for the ANECHOIC Main Skill **and** separately authorized compatibility layers.


for the ANECHOIC Main Skill, the Host Invocation **must** serialize as `$ca` **in** Codex; **if** a Claude compatibility Extension **or** Operator-provided compatibility layer is separately authorized by the Operator, **then** its Host Invocation **must** serialize as `/ca` **in** Claude.
