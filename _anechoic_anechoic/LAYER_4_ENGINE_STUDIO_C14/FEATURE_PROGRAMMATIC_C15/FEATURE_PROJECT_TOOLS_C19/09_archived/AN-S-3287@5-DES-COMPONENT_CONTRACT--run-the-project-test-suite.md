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
  status: archived
  version: 5
  updated_at: '2026-11-22T06:17:29.547354+00:00'
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
The full, unit, and functional phases run these checks before starting any test Module.
Use `--phase static` to run the check on its own.
When `enforce_source_size` is enabled, refuse modules above 300 nonblank
lines or functions above 45 nonblank lines in Python, JavaScript, and
TypeScript source. Use the locked frontend parser for web functions.

## Functional gate

Run `--phase functional` to check the source and run the required non-Docker test Modules configured in `tool.anechoic.test_suite.functional_test_modules` in the Project's `pyproject.toml`.

Refuse empty, invalid, duplicate, or undiscovered selections. A skipped selected test fails the gate. Report the selected Modules and results through the normal Test Suite output.

## Canary

Run `--phase canary` with the Project root, immutable candidate image,
staged package, run ID, and `--canary-selection`. The selection is a JSON
object with `control_root`, `manifest_path`, `manifest_ref`,
`manifest_sha256`, `project_name`, `project_prefix`, and `query_enabled`.

Verify the pinned Manifest before using the staged Project. Start the
candidate, initialize MCP, and run a representative query. Use MCP ping
when the Project excludes Run Query. Report the loopback MCP endpoint
on success and clean up the disposable candidate resources.

## References

AN-S-3055, AN-T-2944, and AN-T-2958.
