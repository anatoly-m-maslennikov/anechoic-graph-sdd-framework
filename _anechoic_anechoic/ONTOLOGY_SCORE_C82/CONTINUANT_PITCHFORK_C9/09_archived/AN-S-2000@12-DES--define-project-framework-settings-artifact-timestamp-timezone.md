---
atom_family: SPEC
atom_id: AN-S-2000
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 12
  updated_at: 2026-10-29 10:03:18 +0400
---
## Summary

Define Project.Framework Settings.Artifact Timestamp Timezone

## Claim scope

the Artifact timestamp timezone setting in Framework Settings.

## Claim

Artifact Timestamp Timezone **means** the Framework Settings value that supplies the timezone interpretation used when emitting Artifact timestamps.

### Formal claim

```text
Entity/Object/Continuant/Structural Unit/Scope Unit/Project.Framework Settings.Artifact Timestamp Timezone[string]{0..1}
```

## Details

Evidence: CA-D-390 supplies the timezone interpretation and its concrete encoding. Candidate #6 keeps Settings attached to Project and keeps concrete ANECHOIC mechanisms in Project Configuration. This definition adds no format, allowed value or default; those remain separate Delivery rules.
