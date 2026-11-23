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
  version: 2
  updated_at: 2026-11-07 15:18:44 +0400
---

## Summary

Declare Project Scope Unit Declaration Form

## Claim

### Prose Claim

Scope Unit Declaration is the Requirement Form for the Project-root Scope Unit Declaration. Its active Subject identifies a Project Scope Unit. Non-Project Scope Units use Scope Delegation.

### Formal Claim

```CFEL
# instances
Atom/(.Header.Form := Scope Unit Declaration)//$root_scope_declaration;
$root_scope_declaration.Header.Role:: [in (Requirement)]{::1};
$root_scope_declaration ((HAS_ACTIVE_SUBJECT)) Scope Unit/Project//$project;
```
