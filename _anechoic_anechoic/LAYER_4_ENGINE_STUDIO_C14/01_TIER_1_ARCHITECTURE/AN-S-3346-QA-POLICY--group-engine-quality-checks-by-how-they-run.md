---
atom_family: SPEC
atom_id: AN-S-3346
container:
  component: C14
tier: 1
context:
  template: POLICY
  lens: QA
state:
  status: active
  version: 4
  updated_at: "2026-11-26T15:27:06.149280+00:00"
---
## Summary

Group Engine quality checks by how they run

## Claim

### Prose Claim

#### Test types and locations

- Static tests belong in the owning `<Owner>__tests/static/`.
- Functional tests belong in the owning `<Owner>__tests/functional/`.
- End-to-end image entry modules belong in the owning
  `<Owner>__tests/image/`. The current runner also accepts root
  `*_docker_e2e.py` and `test_selected_query_mcp_e2e.py` modules in the
  Workbench or MCP test package. Browser case files remain in the owning
  frontend test package.
- Canary checks use the release runner's harness in
  `FEATURE_PROJECT_TOOLS/_release_canary.py`. The harness is separate from
  test-case files and is invoked by the image phase.
- Performance, Load, and optional Soak drivers belong in the owning
  `<Owner>__tests/` package. Performance and Load checks
  are explicitly invoked for relevant changes. Soak checks are explicit
  opt-in checks. These types have no folder-based suite phase.

#### Universal requirements

Every testing type has one owner accountable for maintenance and required
case repair. Each case has one observable guarantee and uses the smallest
supported boundary that verifies it.

Evidence is reproducible for each acceptance guarantee and declared failure
predicate. Data is deterministic and isolated, readiness is observable, and
confirmed regressions remain covered before equivalent cases are removed.
Baseline or regression evidence is captured at the supported boundary before
a behavior-changing refactor or defect fix when feasible.

Each suite report records phase, selection, outcome, and duration under
`.anechoic_tmp/test_reports/`. Profilers are diagnostic only. Equivalent
coverage is not duplicated.

#### Fast Local Release timing

Measure from the first start to production readiness, including fixes and
continuations. The ideal target is 10 minutes. The mandatory performance
limit is 15 minutes. Report whether each target was met. An overrun is a QA
performance miss. Tests and delivery proceed under their normal gates.
