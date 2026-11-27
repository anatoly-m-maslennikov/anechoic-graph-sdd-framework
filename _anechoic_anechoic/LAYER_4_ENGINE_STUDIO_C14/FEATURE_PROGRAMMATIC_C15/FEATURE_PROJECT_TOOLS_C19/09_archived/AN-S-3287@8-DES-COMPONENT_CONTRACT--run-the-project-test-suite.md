---
atom_family: SPEC
atom_id: AN-S-3287
container:
  component: C19
tier: 0
context:
  template: component_contract
  lens: DES
state:
  status: "archived"
  version: 8
  updated_at: "2026-11-26T15:54:01.322685+00:00"
relations:
  ANSWERS:
  - AN-S-3055
  IS_REFERENCE:
  - AN-S-3346
---

## Summary

Run the Project Test Suite

## Guarantee

Given a Project root and an optional selection of source test Modules,
run the discovered or selected tests in fresh Python interpreters.
Report each Module's result and the suite totals on the output streams.

Return zero when the selected suite passes. Return a nonzero status when
selection, the required test environment, or a test Module fails. A
skipped required test fails the suite.

## Static checks

Run Ruff's unused-import check (F401) on the active Python source roots.
Use `--phase static` to run source analysis and tests in `static/`. Run the source analyzers once.
When `enforce_source_size` is enabled, refuse modules above 300 nonblank
lines or functions above 45 nonblank lines in Python, JavaScript, and
TypeScript source. Use the locked frontend parser for web functions.

## Host functional checks

Use `--phase functional` to run the required host Modules configured in
`tool.anechoic.test_suite.functional_test_modules`. Run them in fresh
interpreters. Report the selected Modules and results through the normal
Test Suite output.

Refuse empty, invalid, duplicate, or undiscovered selections. A skipped
required test fails the gate.

Use `--phase unit` to run source-side diagnostic tests and
`--test-module` to focus that run.

## Image tests and canary

Run `--phase image-tests` with the Project root and exact candidate image ID.
Run `--phase canary` for a separate MCP canary on that verified candidate.
The combined `--phase image` runs image tests before the canary.

For the canary, supply the staged package, run ID, and `--canary-selection`.
The selection is a JSON object with `control_root`, `manifest_path`,
`manifest_ref`, `manifest_sha256`, `project_name`, `project_prefix`, and
`query_enabled`. Use `--canary-project-root` for a separate target Project.

Verify the pinned Manifest before using the staged Project. Start the
candidate, initialize MCP, and run a representative query. Use MCP ping
when the Project excludes Run Query. Report the loopback MCP endpoint
on success and clean up the disposable candidate resources.

## References

AN-S-3055, AN-S-4734, AN-T-2944, and AN-T-2958.
