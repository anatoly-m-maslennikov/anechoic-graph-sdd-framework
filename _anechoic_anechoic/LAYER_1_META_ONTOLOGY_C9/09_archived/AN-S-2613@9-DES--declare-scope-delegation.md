---
atom_family: SPEC
atom_id: AN-S-2613
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 9
  updated_at: 2026-11-11 15:25:07 +0400
---
## Summary

Declare Scope Delegation

## Claim

### Prose Claim

Scope Delegation is one generic Form for an external Atom whose Role is in RMEDO. Its active Subject identifies exactly one receiving non-Project Scope Unit within the Project. Its Container is that unit’s one direct structural Parent. Project may contain delegations for its children but is never their receiver. The direct Parent authors the structural declaration and assigns a contribution to the receiving unit; it retains its broader scope and accountability.

For FORMAL_MODEL_ENGINE, the Scope Unit Declaration states the structural facts. For every other Scope Unit, the Scope Delegation is its sole structural declaration and declares:

- Name;
- stable ID;
- ordering state;
- order.number when ordered;
- direct containing Scope Unit.

Label is optional.

Each concrete Scope Delegation Claim lists admitted local Role/Form pairs and typed HAS_ACTIVE_SUBJECT target selections. Plan / Work Report is admitted as a supporting Atom for an already admitted Task. It has that Task’s Container and remains within the applicable Subject selections. Its Role/Form pair needs no separate local listing.

For other local Atoms, admission requires the Header.Container-derived IS_CONTAINED_BY target to be the receiving Scope Unit, the HAS_ACTIVE_SUBJECT target to be in a listed selection, and the Role/Form pair to be listed. Solution, Direct Policy and Approach Policy are RMEDO Forms and require explicit inclusion in the local whitelist. Decision is a MEDO Form.

### Formal Claim

```CFEL
# model
Atom.Header.Context.Form :: Scope Delegation;

# instances
FOR EACH $a[<Atom>, (.Header.Context.Form = Scope Delegation)]:
(
    $a.Header.Context.Role:: [in (Requirement, Method, Evaluation, Delivery, Operations)]{::1};
)
```
