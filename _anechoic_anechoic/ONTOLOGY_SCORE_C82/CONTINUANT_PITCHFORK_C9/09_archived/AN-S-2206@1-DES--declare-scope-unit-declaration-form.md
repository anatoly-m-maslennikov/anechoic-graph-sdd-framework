---
atom_family: SPEC
atom_id: AN-S-2206
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: '2026-11-11T16:37:55+04:00'
---


## Summary

Declare Scope Unit Declaration Form

## Claim

### Prose Claim

Scope Unit Declaration is a Requirement Form. Its active Subject identifies one Scope Unit within the Project. Its Formal Claim states the unit’s stable ID, Name and ordering state. It states order.number when ordered. Label is optional. A non-Project Declaration states the unit’s direct Parent. The Project Declaration identifies the Project root and its unordered state.

### Formal Claim

```CFEL
# model
Atom.Header.Context.Form :: Scope Unit Declaration;

# instances
FOR EACH $a[<Atom>, (.Header.Context.Form = Scope Unit Declaration)]:
(
    $a.Header.Context.Role:: [in (Requirement)]{::1};
    $a ((HAS_ACTIVE_SUBJECT)) Scope Unit//$unit;
)
```
