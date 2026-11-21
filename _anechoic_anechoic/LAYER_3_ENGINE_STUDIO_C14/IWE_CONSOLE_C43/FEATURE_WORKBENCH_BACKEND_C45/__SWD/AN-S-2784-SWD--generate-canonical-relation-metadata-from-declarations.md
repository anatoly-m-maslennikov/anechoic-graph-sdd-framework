---
atom_family: SPEC
atom_id: AN-S-2784
structure:
  container:
    component: C45
  tier: 3
context:
  lens: SWD
state:
  status: "active"
  version: 12
  updated_at: "2026-11-21T13:10:57.653426+00:00"
---
## Summary

Generate canonical relation metadata from declarations

## Claim

### Prose Claim

Use the Model compiled from active native Formal Claims for Workbench canonical Relation names and inverses. Project authored Relation facts using those bindings. Build each declared inverse by reversing its endpoints.

Compile the Model at Project startup. Source refresh updates Relation facts under the loaded Model. Restart to apply changes to the Model.