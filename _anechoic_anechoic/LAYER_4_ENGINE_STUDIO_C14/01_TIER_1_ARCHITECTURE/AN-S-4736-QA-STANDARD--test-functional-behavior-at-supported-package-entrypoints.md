---
atom_family: SPEC
atom_id: AN-S-4736
container:
  component: C14
tier: 1
context:
  template: STANDARD
  lens: QA
state:
  status: active
  version: 1
  updated_at: '2026-11-23T17:59:11Z'
relations:
  IS_REFERENCE:
  - AN-S-3346
  - AN-S-4734
---

## Summary

Test functional behavior at supported Package entrypoints

## Claim

### Prose Claim

#### Required registration and selection

Required Functional cases are explicit entries in
`functional_test_modules`.

Affected-test selection is designed against the last verified baseline. It
selects changed Packages and transitive consumers through imports and declared
CLI, API, and manifest dependencies. The full suite runs when the dependency
graph is unknown or inadequate, or when a shared input affects all Packages.
Selector reports are compared with full-suite runs before adoption. Until the
selection is verified and adopted, the configured required suite is the
release authority.

#### Behavioral requirements

Functional tests use a supported public Package entrypoint. A private Package
is tested through its owning Package. Cases assert actual results, refusals,
and state changes. An isolated real filesystem or database is used when
behavior depends on it. Fakes are used for repeatable external failures.

Before a private-detail test is retired, equivalent requirement coverage is
verified. A narrow stable-module check remains valid for a guarantee that is
difficult to observe at an entrypoint.

#### Runtime

Functional tests run with the locked development runtime and test
dependencies. Profiling is off by default.
