---
atom_family: SPEC
atom_id: AN-S-2625
container:
  component: C43
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: 2026-11-08 22:18:08 +0400
---

## Summary

Declare CODEX_EXTENSION

## Claim

### Prose Claim

The receiving Scope Unit is CODEX_EXTENSION. These permissions apply only to local Atoms whose Header.Container-derived `IS_CONTAINED_BY` target is CODEX_EXTENSION. Its default local admissions remain applicable. Its explicit local Role/Form pairs are Requirement / Entity Definition, Requirement / Rule, Method / Solution, Evaluation / Eval Case, and Delivery / Decision. Each selection is limited to declared model entities or declared instances resolved at [`ANECHOIC_MODEL <+ Workspace`, `ANECHOIC_MODEL <+ View`]. These selections identify endpoint objects, not strings, all members of a type, or descendants. An unresolved address is diagnostic and grants no admission.

### Formal Claim

```CFEL
# instances
Scope Unit//CODEX_EXTENSION.ID == "CA-SU-48";
Scope Unit//CODEX_EXTENSION.Name == "CODEX_EXTENSION";
Scope Unit//CODEX_EXTENSION.Label == "FEATURE";
Scope Unit//CODEX_EXTENSION.order.ordered == false;
Scope Unit//CODEX_EXTENSION ((IS_CONTAINED_BY)) Scope Unit//WORKBENCH
```
