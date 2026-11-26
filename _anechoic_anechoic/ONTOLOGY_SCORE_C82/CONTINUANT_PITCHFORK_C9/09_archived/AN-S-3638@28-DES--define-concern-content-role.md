---
atom_family: SPEC
atom_id: AN-S-3638
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 28
  updated_at: 2026-10-29 17:09:47 +0400
---
## Summary

Define Concern Content Role

## Claim scope

Atom Claims that identify questions, conflicts, **or** problems.

## Claim

Concern Priority classifies handling priority as High, Medium or Low. Selection and conflict-handling policies remain in their governing Claims; this declaration introduces no automatic conflict winner.

A Concern Atom is an Atom with Content Role Concern. Its content identifies one question, conflict or problem; all common Atom meaning, properties and constraints are inherited.

### Formal claim

```text
Entity/Object/Continuant/Governing Objects/Atom/Content Role: Concern.Priority[string]{1}
Entity/Object/Continuant/Governing Objects/Atom/Content Role: Concern.Priority: High
Entity/Object/Continuant/Governing Objects/Atom/Content Role: Concern.Priority: Medium
Entity/Object/Continuant/Governing Objects/Atom/Content Role: Concern.Priority: Low
```
