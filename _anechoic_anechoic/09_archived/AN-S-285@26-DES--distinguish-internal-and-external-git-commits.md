---
atom_family: SPEC
atom_id: AN-S-285
container:
  component: C00
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 26
  updated_at: 2026-10-27 06:04:45 +0400
---
## Summary

Distinguish internal and external Git commits

# Distinguish internal and external Git commits

an internal project commit uses Type Git Commit **and** derives the route `atomic / implementation / internal`.

an outside-owned commit governed as an external input uses Type External Git Commit **and** derives the route `atomic / implementation / external`.

the two Types use the repository-qualified native commit SHA as identity rather than a ANECHOIC artifact sequence. precise repository, author, signer, **and** source facts remain provenance. they do **not** replace the type-derived Governance locus.

## Rationale

distinct names preserve the one-type-to-one-route invariant while retaining the native identity **and** provenance required **to** trace internal **and** outside-owned implementation records.
