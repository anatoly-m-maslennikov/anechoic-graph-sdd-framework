---
atom_family: TKT
atom_id: AN-T-3918
container:
  atom: AN-T-3917
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-24T16:40:34.256033+00:00'
---
## Summary

Assess all import violations

## Work

Use the whole-Project Realization Graph and import lint to inventory every import violation. Include production imports from `*__tests` packages (`code_access_findings` with reason `non-test import from Test Package`).

For each affected scope, choose a rewrite from the ground up or a targeted fix. Record a brief reason and the order of work.

## Assessment

The refreshed 2026-11-24 whole-Project Realization Graph reported 627 import
sites. It reported 450 Code Access denials, 1 non-test import from a Test
Package, 12 undeclared bypasses, 11 unresolved imports, and 153 declared
bypasses. Test Packages account for 421 of the 451 denied sites.

The non-test import is Workbench `playwright.config.ts:2`, which imports
`browser-deadlines` from `FEATURE_WORKBENCH_FRONTEND__tests`. Before the graph
refresh, whole-Project import ownership lint reported zero findings. The Python
child boundary check and Ruff F401 each reported zero findings on 1,223 files.

Studio has 18 tracked JavaScript files, including frontend tests and tooling.
This count excludes historical source samples stored as fixture data.

The site inventory is in `total-refactoring-3918-graph-refresh.json` from MCP
query `475d52012f7f4f4f9d858843aef9994d`. The lint scope and results are in
`total-refactoring-static-summary.json`. The refreshed source-language lint
baseline reports 243 explicit non-Pydantic declarations, 23 authored web
language sites, and no untyped Svelte. Its evidence is in
`total-refactoring-source-languages.json`. All three evidence files are in BB
thread storage.

## Decisions and order

1. **API Backend.** Rewrite one vertical slice through the supported contracts.
   Query a real Project through Web and MCP, then edit a Project file and verify
   that both paths return refreshed results. Reuse the declared peer IPC.
   Keep the existing Kernel, Orchestrator, and Workers until this slice needs a
   replacement.

   Rewrite the MCP bridge for this slice. MCP maps the Backend catalog to its
   transport and forwards requests and results. The Backend owns operation
   policy.

   The live C67–C71 baseline already uses `stack = "beta"`. Put replacements in
   separate `<name>_beta_<new ID>` Components. Add a candidate value to the same
   selector. Build paired baseline and candidate images from the same inputs,
   with the stack choice as the only difference. Keep both available before
   cutover.

2. **Programmatic Model and Graph Rule validation.** Rewrite the validation
   boundary used by Entity Graph and Validate Atoms. Entity Graph imports seven
   validator internals and constructs synthetic validation state. Give both
   callers one owner operation for rule data, exact authority, and diagnostics.

   Apply targeted fixes to the other Model, Tools, and Adapters imports. Keep
   ontology and eDSL algorithm changes with AN2. Correct generated imports at
   their producer and verify the regenerated artifacts and evidence pins.

3. **Workbench, Release, and test harnesses.** Apply targeted fixes. Move the
   browser deadlines dependency to its proper owner. Use Package contracts in
   tests, keep test fixtures in Test Packages, and resolve C74 harness imports
   while preserving historical replay inputs.

4. **Owner imports.** Migrate callers to the defining Package’s `__shared`
   entry. Change ownership or the contract where necessary. Remove redundant
   forwarding. Retain an unrelated declared bypass only when a supported
   contract requires it and the exact caller, provider, and reason are recorded.

## Implementation checks

- Use Pydantic for every structured Python model across the Project. This
  includes internal domain and state models, process, CLI, API, configuration,
  IPC and persistence, external adapters, request and result models, and
  structured models in tests.
  Validate untrusted input on admission, validate once, and reuse accepted
  model instances. Structured models mean named record or object data. Keep
  plain scalar and collection operations ordinary. Follow the existing strict
  pattern in `caller_context.py`, which rejects extra fields on a closed
  contract. Keep AN-S-1913 as the governing reference.
- Use TypeScript for project-authored JavaScript, including tests and tooling.
  Pass the existing 300-line Module and 45-line function checks.
- Run `enforce_source_languages = true` for Beta verification and eventual
  cutover. Run the existing Current baseline in report mode. The mechanical
  checks detect explicit model declarations and authored JavaScript. Review
  ad-hoc structured records through this assessment and AN-T-3919.
- Verify zero graph and import lint violations in the candidate build closure
  before image comparison. Run focused functional tests against the supported
  contracts. Account for every unresolved row and confirm zero non-test imports
  from Test Packages.
- After the focused checks pass, run packaged end-to-end tests and the MCP
  canary once at the end against the candidate image. Compare supported behavior
  with the baseline before cutover.
- After cutover and retirement of the old active source, verify zero violations
  with the whole-Project Realization Graph and import lint.
