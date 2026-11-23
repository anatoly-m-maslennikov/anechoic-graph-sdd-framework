---
atom_family: SPEC
atom_id: AN-S-2584
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 26
  updated_at: 2026-10-29 09:55:37 +0400
---
## Summary

Define Term

## Claim scope

Project-specific vocabulary, including the word `Term` itself.

## Claim

A Term has one Name, the word or phrase used for its meaning. An optional Type classifies a Term where a governing source declares one; it is not required on every Term. This declares the existing vocabulary properties and does not implement or review the deferred Terms Graph.

a Term **means** a word **or** phrase with a Project-specific meaning that remains consistent across **all** its uses **in** the same applicable context.

### Formal claim

```text
Entity/Object/Continuant/Term.Name[string]{1}
Entity/Object/Continuant/Term.Type[string]{0..1}
```

## Details

the word `Term` has the Project-specific meaning defined here, so it is itself a Term. using a Term self-referentially does **not** change its defined meaning **or** require a separate definition layer.
