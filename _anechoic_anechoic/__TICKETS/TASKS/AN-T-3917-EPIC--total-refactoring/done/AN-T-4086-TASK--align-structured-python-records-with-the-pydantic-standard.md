---
atom_family: TKT
atom_id: AN-T-4086
container:
  atom: AN-T-3917
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 1
  updated_at: '2026-11-27T23:42:44+00:00'
---

## Summary

Align structured Python records with the Pydantic standard

## Acceptance

Apply AN-S-1913 to structured Python records across the Project. Resolve blocking model findings and review advisory dictionary candidates. Convert confirmed records and retain ordinary maps. Verify admission and supported wire behavior with focused tests and the normal Static checks.

## Verification

- The Project source-language check reports zero blocking findings.
- The advisory review converted the compiler diagnostic record. The
  other entries are wire payloads, maps, and test fixtures. C91 already
  uses Pydantic admission. Its JSON decode preserves public diagnostics.
- Tool REST passed 7 tests. Methodology passed 29 tests and 9 subtests.
  The Worker publication race test passed in isolation.
- The final source-language scan reports zero blocking findings and
  38 advisory candidates. Write publication state uses a Pydantic
  record. Its focused effect and Ticket tree suites passed 19 tests.
