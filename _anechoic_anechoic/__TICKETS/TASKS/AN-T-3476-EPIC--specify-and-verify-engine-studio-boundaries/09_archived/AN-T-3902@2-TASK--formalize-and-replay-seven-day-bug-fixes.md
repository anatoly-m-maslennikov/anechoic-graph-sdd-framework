---
atom_family: TKT
atom_id: AN-T-3902
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 2
  updated_at: '2026-11-24T11:45:22.222468+00:00'
---
## Summary

Build a golden corpus of seven-day bug fixes

## Work

Build a reusable golden corpus from the confirmed already found and fixed bugs in AN-T-3901. Do not review current code or scan sibling paths. Record exact buggy and fixed revision provenance for each case, or record a gap when it cannot be established.

Independently state expected behavior from requirements and evidence, not from the fix alone. Translate the actual historical buggy and fixed code into Lean where supported. Document the correspondence and abstraction limits.

Measure each supported case in Lean: the exact buggy revision must fail the independent expectation and the fixed revision must pass it. Preserve corpus inputs, commands, revision identifiers, outcomes, and evidence so the corpus can be rerun. Record unsupported translations, missing provenance, and cases that cannot be reproduced.

## Acceptance

A reusable golden corpus records each supported case with exact old and fix provenance, independent expected behavior, code-linked Lean translations, measured old failure and fixed pass, and reproducible commands. It identifies explicit coverage gaps and unsupported or unresolved cases.
