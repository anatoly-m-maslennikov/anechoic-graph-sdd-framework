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
  version: 4
  updated_at: "2026-11-22T15:27:11.920820+00:00"
---
## Summary

Run a pinned Beta snapshot Worker

## Guarantee

Run one pinned build at a time. Start a build at Project startup and
after changes to watched Project sources. Watch code and dependency
inputs when the Project enables its Realization Graph. Offer the generation
to Kernel for admission. Report the active build and latest outcome.
For a rebuild request matching the pinned Project, complete a fresh
generation before replying. Serialize rebuild requests with source changes.
Return the admitted generation or a typed failure.

## References

AN-S-3337 and AN-T-2958.
