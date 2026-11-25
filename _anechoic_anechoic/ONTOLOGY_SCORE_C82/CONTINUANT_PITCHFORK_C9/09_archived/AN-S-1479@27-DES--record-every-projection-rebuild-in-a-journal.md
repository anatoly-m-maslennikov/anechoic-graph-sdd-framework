---
atom_family: SPEC
atom_id: AN-S-1479
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 27
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Record every Projection rebuild in a Journal

## Claim scope

Projection rebuild attempts.

## Claim

**every** Projection rebuild attempt **must** produce append-only Journal provenance from its start through **`=1`** terminal outcome, binding the target Projection, exact source Atom revisions **and** Journal records, generator, configuration, **and** produced revision **when** successful. Programmatic generation **and** LLM generation are provenance facts **only**; the two generation forms grant the Projection no authority.
