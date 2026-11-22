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
  version: 7
  updated_at: "2026-11-22T17:01:49.708112+00:00"
---
## Summary

Run a pinned Beta snapshot Worker

## Guarantee

Run one pinned build at a time. Start a build at Project startup and
after changes to watched Project sources. Watch code and dependency
inputs when the Project enables its Realization Graph. Offer the generation
to Kernel for admission. Report the active build and latest outcome. Retry a build with backoff
when its input changes during capture.
For a rebuild request matching the pinned Project, complete a fresh
generation before replying. Serialize rebuild requests with source changes.
Return the admitted generation and requested result replacements, or a
typed failure. Overlapping requests for the same target share one
admission and result map.

Serialize each accepted Task lifecycle job with generation builds. After
the Worker returns, offer a fresh generation for admission. Reply with
the recorded write outcome and the projection result. Preserve known
effects when admission fails. If the Worker response is lost, report
the write outcome as unknown. Never repeat a write automatically.

## References

AN-S-3337 and AN-T-2958.
