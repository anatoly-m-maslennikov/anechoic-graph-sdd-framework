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
  version: 9
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

For a failed release test phase, record the phase failure.

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


```python trace
declare_trace_contract(
    action='run_release_test_phase', output='failed',
    must_effect=(('C19', 'failed'),),
)
```

```python trace
declare_trace_contract(
    action='run_release_test_phase', output='static_passed',
    must_effect=(('static_checks', 'passed'), ('C19', 'passed')),
    must_precede=((('static_checks', 'passed'), ('C19', 'passed')),),
)
```

```python trace
declare_trace_contract(
    action='run_release_test_phase', output='functional_passed',
    must_effect=(('host_functional_checks', 'passed'), ('C19', 'passed')),
    must_precede=((('host_functional_checks', 'passed'), ('C19', 'passed')),),
)
```

```python trace
declare_trace_contract(
    action='run_release_test_phase', output='image_passed',
    must_effect=(('candidate_image_tests', 'passed'), ('candidate_canary', 'passed'), ('C19', 'passed')),
    must_precede=((('candidate_image_tests', 'passed'), ('candidate_canary', 'passed')), (('candidate_canary', 'passed'), ('C19', 'passed'))),
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
`tool.anechoic.test_suite.functional_test_modules`. Run them locally in fresh
interpreters from their locked virtual environments.

Full runs the required selection. Fast runs every required Module in a Test
Package with an observed failure in the last seven days. It also runs all
required Modules in 10% of the remaining Test Packages, rounded up. Order the
sample by a hash of the Run ID and Package path. Record and reuse the Package
selection on continuation. Keep reports for seven days.

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

Keep checks that can run locally in Functional. Fast image checks cover the
mounted Project, packaged Workbench, and process supervision. The Fast
canary copies the live Project inputs and Manifest. Its copy omits Archives.
