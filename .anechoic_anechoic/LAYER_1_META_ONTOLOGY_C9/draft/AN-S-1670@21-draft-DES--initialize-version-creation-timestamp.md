---
identity:
  atom_id: AN-S-1670
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: draft
  version: 21
  updated_at: '2026-11-13T07:31:04.146015+00:00'
---
## Summary

Initialize Version creation timestamp

## Claim

### Prose Claim

Initialize Updated At to the actual Project-time creation instant when a new Atom Version is created. Accepted business updates, including promotion, use the latest happened_at of the applicable accepted create and update Event Records under CA-R-2567 and the Updated At Declaration. Archival, no-ops and Carrier-only changes preserve Updated At. An ancestor-only move preserves a descendant's Updated At. Timestamp encoding follows CA-D-270.
