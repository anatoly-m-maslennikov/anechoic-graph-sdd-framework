---
atom_family: SPEC
atom_id: AN-S-2591
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: 2026-11-07 15:18:44 +0400
---

## Summary

Declare Atom.Header.Tier.Label

## Claim

### Formal Claim

```CFEL
# model
Atom.Header.Context.Tier.Label:: [string]{::0..1};

Atom.Header.Context.Tier.Label.*[]{::0};

# instances
Atom//$atom_2;

IF (($atom_2.Header.Context.Tier.Label{=1}) AND ($atom_2.Header.Context.Tier = 1)) THEN ($atom_2.Header.Context.Tier.Label == Core);

Atom//$atom_3;

IF (($atom_3.Header.Context.Tier.Label{=1}) AND ($atom_3.Header.Context.Tier = 2)) THEN ($atom_3.Header.Context.Tier.Label == General);

Atom//$atom_4;

IF (($atom_4.Header.Context.Tier.Label{=1}) AND ($atom_4.Header.Context.Tier = 3)) THEN ($atom_4.Header.Context.Tier.Label == Standard);

Atom//$atom_5;

IF (($atom_5.Header.Context.Tier.Label{=1}) AND ($atom_5.Header.Context.Tier = 4)) THEN ($atom_5.Header.Context.Tier.Label == Detail)
```
