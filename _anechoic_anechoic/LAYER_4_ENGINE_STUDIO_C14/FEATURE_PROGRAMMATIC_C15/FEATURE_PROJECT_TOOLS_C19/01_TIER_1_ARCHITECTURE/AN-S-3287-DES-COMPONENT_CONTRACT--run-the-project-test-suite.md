---
atom_family: SPEC
atom_id: AN-S-3287
container:
  component: C19
tier: 1
context:
  template: component_contract
  lens: DES
state:
  status: active
  version: 6
  updated_at: '2026-11-22T16:11:02.638533+00:00'
relations:
  IS_REFERENCE:
  - AN-S-3346@1
---

## Summary

Run the Project Test Suite

## Guarantee

Given a Project root and an optional selection of source test Modules,
run the discovered or selected tests in fresh Python interpreters.
Report each Module's result and the suite totals on the output streams.

Return zero when the selected suite passes. Return a nonzero status when
selection, the required test environment, or a test Module fails. A
skipped required integration test fails the suite.

## Static checks

Run Ruff's unused-import check (F401) on the active Python source roots.
Use `--phase static` to run source analysis and tests in `static/`. Run the source analyzers once.
When `enforce_source_size` is enabled, refuse modules above 300 nonblank
lines or functions above 45 nonblank lines in Python, JavaScript, and
TypeScript source. Use the locked frontend parser for web functions.

## Unit tests

Run `--phase unit` for source-side tests. Use `--test-module` for a focused run. Use `--required` for the host test Modules configured in `tool.anechoic.test_suite.functional_test_modules`.

Refuse empty, invalid, duplicate, or undiscovered selections. A skipped selected test fails the gate. Report the selected Modules and results through the normal Test Suite output.

## Image tests

Run `--phase image` with the Project root, immutable candidate image,
staged package, run ID, and `--canary-selection`. The selection is a JSON
object with `control_root`, `manifest_path`, `manifest_ref`,
`manifest_sha256`, `project_name`, `project_prefix`, and `query_enabled`.

Run image tests against that candidate. Run the canary only after the image tests pass. Verify the pinned Manifest before using the staged Project. Start the
candidate, initialize MCP, and run a representative query. Use MCP ping
when the Project excludes Run Query. Report the loopback MCP endpoint
on success and clean up the disposable candidate resources.

## References

AN-S-3055, AN-T-2944, and AN-T-2958.
