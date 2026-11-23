---
atom_family: SPEC
atom_id: AN-S-2184
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-03 20:00:05 +0400
---
## Summary

Declare Atom.Header.Subjects.Passive

## Claim

### Prose Claim

Dependencies identify direct contextual dependencies.

### Formal Claim

```CFEL
# model
Atom.Header.Context.Topics.Dependencies{::0..1}:: [string]{::0+};

Atom.Header.Context.Topics.Dependencies.*[]{::0};

# instances
$atom[<Atom>];

COUNT(VALUES($atom.Header.Context.Topics.Dependencies)) = COUNT(DISTINCT VALUES($atom.Header.Context.Topics.Dependencies))
```
