---
atom_family: SPEC
atom_id: AN-S-60
container:
  component: C16
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 16
  updated_at: 2026-10-24 02:14:24 +0400
---
## Summary

Classify rename as UPDATE

# Classify rename as UPDATE

## Claim checked

a filename-only rename **without** Structural relocation is recorded as `UPDATE`. a claim that this is a same-identity, Version-preserving carrier-only change requires the preservation conditions **in** CA-R-1433 **and** CA-D-304; physical change classification alone does **not** prove semantic conformance.

## Test cases

- supply a trigger for a permitted Carrier-only filename correction. preserve content, Atom identity, Summary, Atom Scope, Claim Scope, authored semantic Relations, Structural location, **and** Version. the correction changes encoding **only**, **not** the Summary value.
- separately observe a filename Summary Slug change **or** changed heading that actually changes the Summary while retaining the assigned ID. preserve that observed inconsistency; do **not** classify it as a valid same-identity Summary revision under CA-R-1464.
- supply an observation that includes a changed Version **or** content. retain the actual change rather than forcing it into the unchanged-Version fixture **or** inventing a prior state.

## Acceptance criteria

- the valid Carrier-only fixture reports `UPDATE`, records both filenames **and** observed Version, **and** does **not** report Structural `MOVE`.
- a changed Summary requires a new Atom ID through the separately authorized replacement workflow; context gathering **must not** invent that successor **or** perform replacement.
- context preserves actual before/after filenames, Revisions, **and** unresolved identity evidence under CA-R-804. an observed Project-conformance defect does **not** block historical Journal recording **or** authorize changing the subject.
- Version preservation is checked **only** for the fixture that satisfies CA-R-1433, **not** imposed on **every** observed rename. lossless classification does **not** certify an invalid Atom.

## Failure disposition

reject a realization that loses evidence, invents a replacement identity, misreports Structural relocation, treats a changed Summary as valid under the same identity, **or** rejects intact historical observations solely for Project nonconformance. preserve the exact observation **and** distinguish classification from conformance results.
