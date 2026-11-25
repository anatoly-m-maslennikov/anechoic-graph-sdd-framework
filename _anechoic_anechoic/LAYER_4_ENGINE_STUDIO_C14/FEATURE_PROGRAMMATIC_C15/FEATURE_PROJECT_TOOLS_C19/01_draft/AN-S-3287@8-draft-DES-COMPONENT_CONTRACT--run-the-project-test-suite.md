---
atom_family: SPEC
atom_id: AN-S-3287
container:
  component: C19
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3055
state:
  status: draft
  version: 8
  updated_at: '2026-11-25T09:04:52Z'
---

## Summary

Run the Project Test Suite

## Guarantee

Given a Project root and an optional selection of source test Modules,
run the discovered or selected tests in fresh Python interpreters.
Report each Module's result and the suite totals on the output streams.

## Claim

### Prose Claim

`succeeded` means the selected suite passes. `failed` includes selection
failure, failure of the required test environment, a failed test Module,
or a skipped required test.

`zero` denotes process exit status 0. `nonzero` denotes any other process exit status.

### Formal Claim

```python cli
declare_cli_contract(
    interface='test_suite',
    action='run_project_test_suite',
    runner='uv',
    path='LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/test_suite__pub.py',
    outcomes={'succeeded': 'zero', 'failed': 'nonzero'},
)
```

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

Refuse empty, invalid, duplicate, or undiscovered selections.

Use `--phase unit` to run source-side diagnostic tests and
`--test-module` to focus that run.

## Image tests

Run `--phase image` with the Project root, immutable candidate image,
staged package, run ID, and `--canary-selection`. The selection is a JSON
object with `control_root`, `manifest_path`, `manifest_ref`,
`manifest_sha256`, `project_name`, `project_prefix`, and `query_enabled`.

Run image tests against that candidate. Run the canary only after the image tests pass. Verify the pinned Manifest before using the staged Project. Start the
candidate, initialize MCP, and run a representative query. Use MCP ping
when the Project excludes Run Query. Report the loopback MCP endpoint
on success and clean up the disposable candidate resources.
