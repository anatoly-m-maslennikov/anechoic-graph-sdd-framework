---
atom_family: TKT
atom_id: AN-T-1582
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 6
  updated_at: 2026-10-24 08:22:45 +0400
---
## Summary

Add Project **and** image launcher golden tests

# Summary

Add Project **and** image launcher golden tests

## Objective

the AI Agent creates the test-first golden corpus for Project selection **and** image admission.

## Details

- input: the reviewed RMED **and** accepted selection/image cases; reuse the existing Docker runtime test infrastructure.
- output: deterministic fixtures **and** mocked tests for two repositories, two Projects **in** one repository, ambiguous selection, unsafe bindings, dropped selection during Gateway spawn, a valid source frontier bound **to** the wrong Project, absent images, compatible-image reuse, stale code, **and** build failure.
- verification: run the bounded tests **before** implementation; distinguish expected failures demonstrating missing behavior from invalid fixtures.
- effort: **`<=15`** minutes for **`=1`** AI Agent; the Epic's decomposition rule applies **before** execution **if** the estimate no longer holds.

### Definition of Done

- completion evidence: selection **and** image executable golden fixtures; expected missing-module test-first failures saved **in** `.anechoic_tmp/launcher-epic-1829/pre-implementation-selection-images.md`; source-change, immutable default-build reinspection **and** foreign-context cases added following review.

the Plan is **not** Done **if** ((a listed selection **or** image case is absent) **or** (the fixtures depend on live Project secrets **or** mutable host state) **or** (the pre-implementation test result is missing)).
