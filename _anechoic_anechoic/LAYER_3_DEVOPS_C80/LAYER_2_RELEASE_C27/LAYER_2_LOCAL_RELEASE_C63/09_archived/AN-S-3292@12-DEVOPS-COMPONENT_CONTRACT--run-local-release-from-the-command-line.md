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
  version: 12
  updated_at: '2026-11-24T18:03:32.256316+00:00'
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

Use the host command in AN-S-3288. Checkpoint Git only for a direct release.
A fresh direct release bumps the candidate version. Package Active source Atoms.

Use the Test Suite for release checks. Before long gates, launch pinned
Chromium, load pinned DuckPGQ, and check locked frontend dependencies. Use
installed dependencies. Report failed prerequisites with cache paths or setup
steps. Run Static, then required host Functional. Build the candidate after
both pass. Run its image suite, then its MCP canary, as separate checkpoints.
`--test-module` keeps both host gates.

Use `prepare-local` with an exact base commit, literal changed paths, and an
isolated loopback port. Report the private checkout revision for Local Release.

`verify-image` builds the canary package and exact image at the source version.
Run the required image suite and MCP canary. End verification with results
and retained evidence.

A split run needs a clean checkout at the full source SHA and a managed target.
Use the source version and read-only Git histories. Run host gates on the
source. Test the exact target-owned candidate image. Run its MCP canary in a
disposable target context.

After all gates pass, install the package and its `ane` Skill. Preserve
target authoring inputs, Manifest settings, configuration, and Project data.
Start on the target Manifest port. Tag production after MCP is ready. Apply
AN-S-4733 and report incomplete cleanup separately from promotion failure.

Stop and report each failure. The Operator can fix the inputs and explicitly
continue the same run any number of times. Keep the Run ID, Project bindings,
and allocated version. Before delivery starts, record the current exact source
revision and accept a corrected split SHA from the same source checkout.

Save progress and evidence atomically. Reuse each passing phase only after
its input digests and required evidence match. Keep the source revision of
each retained result and the source revision used to build the image. Continue
at the earliest incomplete or invalidated phase. Protect artifacts of open runs.

When only MCP canary inputs change, reuse the verified image and image suite.
When runtime image inputs change, build a new image, run its image suite, and
run its MCP canary. Shared input changes invalidate each phase that uses them.

After delivery starts, reconcile installed files and runtime identity with
the recorded artifact before repeating a delivery effect. Report unverifiable
state. After verified promotion, resume pending cleanup alone.

Pin the accepted source revision, image build revision, exact image ID and
fingerprint, target Project identity, and verified container readiness in the
result and receipt. Keep receipts under
`.anechoic_runtime/simple_local_release/` and Run ID test logs under `.anechoic_tmp/simple_local_release/`.

Report the failed step and observed effects. If initial selection fails,
report `validate_project_selection` with no effects. After failed production
startup, capture bounded container state and recent logs before cleanup.
Report the affected Docker port or resource. Apply cleanup ownership checks.

## References

AN-S-3290 and AN-S-4734.
