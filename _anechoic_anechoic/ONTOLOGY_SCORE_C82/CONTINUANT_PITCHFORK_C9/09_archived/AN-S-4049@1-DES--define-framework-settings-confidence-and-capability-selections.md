---
atom_family: SPEC
atom_id: AN-S-4049
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-29 09:55:37 +0400
---
## Summary

Define Framework Settings confidence and capability selections

## Claim

Framework Settings may explicitly override the necessary-information and semantic-resolution confidence defaults as integer percentages. Their effective defaults remain Operator-configurable under CA-R-1652 and CA-R-380; absence of an explicit value preserves the governed default resolution.

Tool Selections groups the selected active/background capabilities and their per-capability settings. Extension Selections groups enabled or disabled installed Extensions, selected Versions where applicable, and retained per-Extension settings. These are structured groups with no direct scalar value; retaining settings does not enable a disabled Extension. Their internal declarations remain governed by applicable D authority, not a new generic schema.

### Formal claim

```text
Project.Framework Settings.Confidence.Necessary Information Threshold[int]{0..1}
Project.Framework Settings.Confidence.Semantic Resolution Threshold[int]{0..1}
Project.Framework Settings.Tool Selections{0}
Project.Framework Settings.Extension Selections{0}
```

## Details

CA-D-368, CA-D-369, CA-D-372 and CA-D-373 retain their serialization requirements. No current Settings value changes, unknown field migration, Tool catalog or Extension object is introduced. C613 tracks the minimal shared-schema continuation.
