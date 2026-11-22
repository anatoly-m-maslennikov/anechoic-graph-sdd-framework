---
atom_family: SPEC
atom_id: AN-S-3345
container:
  component: C00
tier: 2
context:
  lens: QA
relations:
  IS_REFERENCE:
  - AN-S-3346@1
  - AN-S-3287@6
  - AN-S-3292@5
state:
  status: draft
  version: 1
  updated_at: '2026-11-22T16:11:02.638533+00:00'
---

## Summary

Verify the three Project test entry points

## Claim

### Prose Claim

The ANECHOIC Project shall expose exactly three Test Suite entry points.

- `static` checks source and tests the analyzers without running the application or building an image.
- `unit` runs source-side tests without a candidate image. It includes required host-side integration and functional checks.
- `image` runs functional, end-to-end, and canary checks against the same immutable candidate image in disposable containers.

Verify that each new or moved check is in its owning `<Component>__tests/` Package under `static/`, `unit/`, or `image/`.

Verify that each entry runs independently and reports its scope and result. A failed or incomplete required check returns a nonzero status. Identify focused runs as focused.

Verify that Local Release uses the same entries. Run static and required source-side tests before the build. Run image tests against the exact image proposed for installation. Install only after all required checks pass.
