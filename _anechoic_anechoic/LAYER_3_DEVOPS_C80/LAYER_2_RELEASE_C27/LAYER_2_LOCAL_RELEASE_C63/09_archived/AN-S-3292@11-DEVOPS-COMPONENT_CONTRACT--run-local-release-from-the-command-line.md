---
atom_family: SPEC
atom_id: AN-S-3292
container:
  component: C63
tier: 0
context:
  template: component_contract
  lens: DevOps
state:
  status: archived
  version: 11
  updated_at: '2026-11-24T13:51:38.603869+00:00'
relations:
  ANSWERS:
  - AN-S-3290
  IS_REFERENCE:
  - AN-S-4733
  - AN-S-4734
  - AN-S-3346
  - AN-S-3287
---

## Summary

Run Local Release from the command line

## Guarantee

Use the host command in AN-S-3288. A fresh same-Project release checkpoints Git
and bumps the candidate version. Package Active source Atoms.

Use the Test Suite before long gates. Launch pinned Chromium, load pinned
DuckPGQ, and check locked frontend dependencies. Use installed dependencies.
Report failed prerequisites with cache paths or setup steps. Run Static then
required host Functional before build. `--test-module` keeps both gates.

Use `prepare-local` with an exact base commit, literal changed paths, and an
isolated loopback port. Report the private checkout revision for Local Release.

`verify-image` builds the canary package and exact image at the source version.
Run the required image suite and canary. End with results and retained evidence.

An explicit target needs a clean checkout at the full source SHA and a managed
target. Use the source version and read-only Git histories. Run host gates on
the source and the image gate on the exact target-owned candidate. Use a
disposable target context for its canary.

After all gates pass, install the package and its `ane` Skill. Preserve
target authoring inputs, Manifest settings, configuration, and Project data.
Start on the target Manifest port. Tag production after MCP is ready. Apply
AN-S-4733 and report incomplete cleanup separately from promotion failure.

Resume with the original Run ID, Project bindings, and explicit source revision
when supplied. Keep the candidate version, record progress and evidence
atomically, and protect artifacts of open runs.

Verify retained inputs, phase evidence, installed files, and runtime identity
before reuse. Continue at the earliest incomplete or invalidated phase. Repeat
affected checks before installation. Report unverifiable runs or state.
After verified promotion, resume pending cleanup alone.

Pin the source revision, exact image ID and fingerprint, target Project identity,
and verified container readiness in the result and receipt. Keep receipts under
`.anechoic_runtime/simple_local_release/` and Run ID test logs under `.anechoic_tmp/simple_local_release/`.

Report the failed step and observed effects. If initial selection fails,
report `validate_project_selection` with no effects. After failed production
startup, capture bounded container state and recent logs before cleanup.
Report the affected Docker port or resource. Apply cleanup ownership checks.

## References

AN-S-3290 and AN-S-4734.
