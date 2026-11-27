---
atom_family: SPEC
atom_id: AN-S-4734
container:
  component: C14
tier: 1
context:
  template: STANDARD
  lens: QA
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-27T14:45:10.285943+00:00"

---

## Summary

Run the Engine release test gates in order

## Claim

### Prose Claim

Use the C19 Test Suite phases in AN-S-3287. When the selected suite exposes
separate phases, Local Release records independent image suite and canary
results for the exact candidate.

#### Gate order

1. Run Static source analysis and analyzer tests under AN-S-3287.
2. Run the required host Functional cases selected by the configured required
   suite in the locked development environment.
3. Build the exact isolated production candidate image.
4. Run End-to-End checks against that immutable candidate before installation.
5. Run the candidate Canary after the image checks pass and before
   installation.
6. Install the candidate after all required checks pass.

Apply AN-S-4731 to image liveness and deadlines.

Any failed or incomplete required check stops the release before the next
step.
