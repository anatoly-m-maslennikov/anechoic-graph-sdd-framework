---
subjects:
  active: ANECHOIC_MODEL <+ Atom.Header.State.Updated At
  passive:
  - ANECHOIC_MODEL <+ Atom
  - ANECHOIC_MODEL <+ Atom.Header.State.Status
  - ANECHOIC_MODEL <+ Carrier
  - ANECHOIC_MODEL <+ Carrier.Canonical Address
version: 19
updated_at: 2026-11-03 20:57:46 +0400
relations:
  child_of:
  - CA-R-1416
atom_id: CA-R-1788@19-draft
status: Draft
tier: 3
role: Requirement
form: Rule
---
## Summary

Initialize Version creation timestamp

## Claim

### Prose Claim

Initialize Updated At to the actual Project-time creation instant when a new Atom Version is created. In-place edits, Status-only changes, archival, and promotion preserve the existing Version's Updated At. An ancestor-only move also preserves a descendant's Updated At. Timestamp encoding follows CA-D-270.
