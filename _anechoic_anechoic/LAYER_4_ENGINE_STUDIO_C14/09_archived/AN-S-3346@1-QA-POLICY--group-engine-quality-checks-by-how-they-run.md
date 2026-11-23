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
  status: "archived"
  version: 1
  updated_at: "2026-11-23T01:48:06.198587+00:00"
---

## Summary

Group Engine quality checks by how they run

## Claim

### Prose Claim

Expose three independent Engine Test Suite entry points.

- `static` runs source analysis and tests of the analyzers.
- `unit` runs source-side unit and integration tests.
- `image` runs functional, end-to-end, and canary tests against one immutable candidate image.

Put new or moved checks under the corresponding `static/`, `unit/`, or `image/` subfolder in the owning `<Component>__tests/` Package. Discover existing flat host tests as unit tests.

Run static checks and required unit tests before building for Local Release. Run image tests before installing the candidate. Report the failed or incomplete check and stop the release.
