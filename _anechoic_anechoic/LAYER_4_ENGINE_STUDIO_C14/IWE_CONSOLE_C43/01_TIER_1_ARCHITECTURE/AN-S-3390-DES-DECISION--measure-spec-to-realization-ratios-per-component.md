---
atom_family: SPEC
atom_id: AN-S-3390
container:
  component: C43
tier: 1
context:
  template: DECISION
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-23T01:48:06.213818+00:00'
---

## Summary

Measure Spec to Realization ratios per Component

## Claim

### Prose Claim

For each Component, count its directly owned Current Spec carriers and authored Realization. Exclude descendant Components from the parent's count. Use the Realization Graph's Test Package relations and the file classification in AN-S-3014. Leave files without a mechanical classification out of the split.

Report Spec size in decimal kB with the header, and in kB and lines for the body alone. For each Spec measure, divide by the corresponding Realization measure for these populations.

- Implementation.
- Test code.
- Test assets, including corpora.
- Total tests.
- Implementation and total tests.

Count physical lines in text. Count binary assets by bytes only. Leave ratios with a zero denominator empty.
