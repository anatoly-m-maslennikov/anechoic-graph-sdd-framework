---
atom_family: SPEC
atom_id: AN-S-4320
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: 2026-11-11 14:06:22 +0400
---

## Summary

Declare Project Scope Unit Declaration Form

## Claim

### Prose Claim

Scope Unit Declaration is the Requirement Form for the Project-root Scope Unit Declaration. Its active Subject identifies a Project Scope Unit. Non-Project Scope Units use Scope Delegation.

### Formal Claim

```CFEL
# model
Atom.Header.Context.Form :: Scope Unit Declaration;

# instances
FOR EACH $a[<Atom>, (.Header.Context.Form = Scope Unit Declaration)]:
(
    $a.Header.Context.Role:: [in (Requirement)]{::1};
    $a ((HAS_ACTIVE_SUBJECT)) Scope Unit/Project//$project;
)
```
