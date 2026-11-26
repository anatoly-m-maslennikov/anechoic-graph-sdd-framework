---
atom_family: SPEC
atom_id: AN-S-2686
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 23
  updated_at: 2026-10-24 01:37:42 +0400
---
## Summary

Bind traceability to exact claims and revisions

# Summary

Bind traceability to exact claims and revisions

## Scope

ANECHOIC traceability assertions.

## Claim

**every** ANECHOIC traceability assertion **must** identify the exact governed claim revision on which a receiving artifact, implementation target, evaluation use, delivery action, operational observation, **or** other governed result relies.

## Details

the trace **must** preserve the source identity **and** accepted Revision, the receiving identity **or** stable target locator, the typed relation between them, the bounded scope **and** use, **and** the provenance needed **to** replay that relation. a relation **to** an artifact ID **without** its relied-upon revision is insufficient **after** the Atom has more than one accepted Revision.

Traceability records relationships; it does **not** transfer authority **or** prove correctness, execution, delivery, **or** currentness. secondary storage history **may** preserve Carrier evidence, while governed Journals preserve semantic relationships independently of that secondary history.
