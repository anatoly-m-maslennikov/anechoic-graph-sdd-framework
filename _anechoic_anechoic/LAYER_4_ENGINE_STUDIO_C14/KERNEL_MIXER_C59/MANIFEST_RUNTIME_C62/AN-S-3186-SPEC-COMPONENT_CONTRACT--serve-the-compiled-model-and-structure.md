---
atom_family: SPEC
atom_id: AN-S-3186
container:
  component: C62
tier: 0
context:
  template: component_contract
  lens: SPEC
relations:
  ANSWERS:
  - AN-S-3088
state:
  status: active
  version: 4
  updated_at: '2026-11-22T22:21:58.190550+00:00'
---

## Summary

Serve the compiled Model and Structure

## Guarantee

For a selected native Project, host the admitted Model and validated
Structure in the Kernel process. Provide the compiled Model directory,
bound Model, and Structure snapshot path after verifying that the Model
and initial Structure share one Model source fingerprint.

Run the Manifest Builder in a bounded separate process. On relevant
Manifest changes, validate each replacement Structure against the admitted
Model and publish it atomically. Keep the last accepted Structure if a
rebuild fails. Admit a changed Model on restart.

## References

AN-S-3088, AN-S-3089, AN-S-3090, AN-S-3091, and AN-T-2947.
