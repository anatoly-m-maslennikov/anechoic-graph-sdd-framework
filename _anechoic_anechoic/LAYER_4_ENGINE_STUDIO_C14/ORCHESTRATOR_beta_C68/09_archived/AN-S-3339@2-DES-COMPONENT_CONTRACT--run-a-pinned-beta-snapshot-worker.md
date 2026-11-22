---
atom_family: SPEC
atom_id: AN-S-3339
container:
  component: C68
tier: 1
context:
  template: component_contract
  lens: DES
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-22T13:08:06.934512+00:00"
---
## Summary

Run a pinned Beta snapshot Worker

## Guarantee

Run one pinned build at a time. Start a build at Project startup and
after changes to watched Project sources. Offer the completed generation
to Kernel for admission. Report the active build and latest outcome.

## References

AN-S-3337 and AN-T-2958.
