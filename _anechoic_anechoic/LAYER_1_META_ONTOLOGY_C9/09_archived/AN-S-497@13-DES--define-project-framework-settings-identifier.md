---
atom_family: SPEC
atom_id: AN-S-497
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 13
  updated_at: 2026-10-29 10:03:18 +0400
---
## Summary

Define Project.Framework Settings.Identifier

## Claim scope

the identifier of the Project's authoritative Framework Settings configuration.

## Claim

Framework Settings Identifier identifies the Project's authoritative Framework Settings configuration, **not** an Atom.

### Formal claim

```text
Entity/Object/Continuant/Structural Unit/Scope Unit/Project.Framework Settings.Identifier[string]{1}
```

## Details

Evidence: CA-R-1402 defines the owning configuration; CA-R-1404 keeps it outside the Atom type; CA-D-358 supplies its concrete identifier. Candidate #6 decision 11 places Project under Continuant; concrete ANECHOIC identity encodings belong in Project Configuration. This definition does not duplicate the concrete identifier spelling or create an Atom ID.
