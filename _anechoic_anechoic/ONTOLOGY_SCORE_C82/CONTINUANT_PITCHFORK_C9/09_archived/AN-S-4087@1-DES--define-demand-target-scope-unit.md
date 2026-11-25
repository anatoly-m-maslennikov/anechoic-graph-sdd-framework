---
atom_family: SPEC
atom_id: AN-S-4087
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-29 17:09:47 +0400
---
## Summary

Define Demand Target Scope Unit

## Claim scope

The Claim Target Scope Unit property of a Demand Atom.

## Claim

Demand.Target Scope Unit **means** the resolved Claim Target Scope Unit carried by a Demand Atom; it identifies the Producer Scope Unit whose results that Demand constrains. When carried, it is the explicit top-level YAML string `claim_target_scope_unit` and resolves to one registered Scope Unit. It is not Claim Scope, another Local Scope Unit, or a value inferred from a Carrier location. A complete Current Demand Carrier follows the applicable resolution and carrying rules.

### Formal claim

```text
Entity/Object/Continuant/Governing Objects/Atom/Content Role: Requirement/Type: Demand.Target Scope Unit[string]{0..1}
```
