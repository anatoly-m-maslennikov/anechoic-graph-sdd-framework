---
atom_family: SPEC
atom_id: AN-S-4165
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

Define Evaluation Status

## Claim scope

Lifecycle status of an Evaluation Atom.

## Claim

Evaluation Status is the one-string lifecycle classification of an Evaluation Atom; it inherits Draft, Active and Archived under the applicable status model, with the Core Evaluation Status model admitting exactly those values.

### Formal claim

```text
Entity/Object/Continuant/Governing Objects/Atom/Content Role: Evaluation.Status[string]{1}
```

## Details

Source meaning: CA-R-1989, CA-R-655, CA-R-1398. Scope-specific constraints remain in their governing Rs.
