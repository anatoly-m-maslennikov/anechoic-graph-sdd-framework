---
atom_family: SPEC
atom_id: AN-S-2313
container:
  component: C58
tier: 4
context:
  lens: DOM/MTD
state:
  status: "active"
  version: 4
  updated_at: "2026-11-25T23:05:43.990705+00:00"
---
## Summary

Validate Atom Claims and derived Projections

## Claim

### Prose Claim


active and draft Atom Claims, their Summaries, and requested Translation and terminology Projections.


Check Active and Draft Atoms against their applicable Template and writing rules. When the Template requires a Claim, it must express one precise contribution. Check the source-faithful Summary and each requested Translation or terminology Projection. A missing optional Projection is valid when nobody requested it.

## Details

### Test case

Use valid Active and Draft fixtures for the applicable Templates. Exercise both Templates that require a Claim and those with another primary section. include fixtures with no requested Translation **or** terminology Projection **and** fixtures with requested Projections. derive a candidate Summary during Atom creation, **then** retain it for checks of subsequent Revisions under AN-S-1604. derive requested Translation **and** terminology Projections twice **without** regenerating the existing Atom's Summary. **then** introduce ambiguity, an unstated participant, two independent Claims, an added Projection meaning, an independent vocabulary entry, **and** a confidence result below the effective Confidence Threshold resolved according **to** AN-S-1702.

### Acceptance criteria

**every** valid fixture has **`=1`** precise interpretation, a source-faithful Summary, **and** reproducible Projections **when** requested. no fixture fails merely because an optional Projection was **not** requested. **every** invalid fixture fails. a confidence result below the effective Confidence Threshold leaves the Atom unchanged **and** requests Operator disposition. changing the applicable Operator input, declared work override, enclosing override, **or** applicable configuration default changes the checked threshold according **to** AN-S-1702 **without** retaining a fixed percentage gate.

### Failure disposition

record a Concern naming the affected Claim **or** Projection.
