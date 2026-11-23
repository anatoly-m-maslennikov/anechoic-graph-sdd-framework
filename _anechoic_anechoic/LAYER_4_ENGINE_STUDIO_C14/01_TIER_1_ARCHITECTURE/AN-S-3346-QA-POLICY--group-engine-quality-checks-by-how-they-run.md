---
atom_family: SPEC
atom_id: AN-S-3346
container:
  component: C14
tier: 1
context:
  template: POLICY
  lens: QA
state:
  status: "active"
  version: 2
  updated_at: "2026-11-23T01:48:06.199176+00:00"
---
## Summary

Group Engine quality checks by how they run

## Claim

### Prose Claim

Expose independent `static`, `unit`, and `image` Engine Test Suite entry points. Static runs source analysis, including unused imports and the applicable 300/45 source-size checks, and analyzer tests under the Project Test Suite contract. Unit runs source-side unit and integration tests. Image runs functional, end-to-end, and canary tests against one immutable candidate.

Place new or moved checks in the matching `static/`, `unit/`, or `image/` subfolder of the owning `<Component>__tests/` Package. Discover existing flat host tests as unit tests.

Run static and required unit checks before a Local Release build. Run image checks before installation. Stop release on failed or incomplete required checks. Cover confirmed regressions at a real interface. Retire a unit test only after behavioral coverage of its guarantee exists.

For image startup and indexing, observe process and Worker liveness and allow an exact active run to be aborted. Do not fail a live run solely for elapsed time. Record elapsed time separately. Aim for 0.25 s visibility on a single Ticket change and measure a 500-Atom batch separately.
