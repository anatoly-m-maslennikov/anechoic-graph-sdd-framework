---
atom_family: SPEC
atom_id: AN-S-2183
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: 2026-11-05 22:47:24 +0400
---
## Summary

Declare Atom.Header

## Claim

### Prose Claim

Atom.Header groups the Atom Properties carried in YAML frontmatter, including for Draft Atoms.

### Formal Claim

```CFEL
# model
Atom.Header{::1}:: []{::0};

Atom.Header.*[string,in(ID, Ref ID, Role, Form, Version, Status, Updated At, Label, Tier, Topics, Container, Relations, Carrier Destination, Priority, AI Agent Confidence Threshold, Work Sequence Number)]{::0+};

Atom.Header.ID ;> Atom.Header.Ref ID;

Atom.Header.Ref ID ;> Atom.Header.Container;

Atom.Header.Container ;> Atom.Header.Role;

Atom.Header.Role ;> Atom.Header.Form;

Atom.Header.Form ;> Atom.Header.Label;

Atom.Header.Label ;> Atom.Header.Topics;

Atom.Header.Topics ;> Atom.Header.Tier;

Atom.Header.Tier ;> Atom.Header.Relations;

Atom.Header.Relations ;> Atom.Header.Status;

Atom.Header.Status ;> Atom.Header.Version;

Atom.Header.Version ;> Atom.Header.Updated At;

Atom.Header.Updated At ;> Atom.Header.Carrier Destination
```

