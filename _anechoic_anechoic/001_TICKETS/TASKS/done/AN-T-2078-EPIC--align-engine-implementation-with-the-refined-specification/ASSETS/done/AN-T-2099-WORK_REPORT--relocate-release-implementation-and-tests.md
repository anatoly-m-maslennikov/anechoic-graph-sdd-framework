---
atom_family: TKT
atom_id: AN-T-2099
container:
  atom: AN-T-2078
priority: 2
context:
  template: work_report
state:
  status: done
  version: 1
  updated_at: 2026-11-11 00:44:42 +0400
---

## Summary

Relocate release implementation and tests

## Details

Promoted six independently reviewed exact-path corrections and moved 25 release-specific implementation/test files to LAYER_5_FRAMEWORK_DELIVERY. Package-local public tests remain under PUBLIC_RELEASE/tests. Shared Engine helpers stay in place; updated suite discovery, fixture import and README commands. Independent review caught and corrected one focused-test example path.

Passed 88 local and 12 public release tests and both CLI help checks; integration passed 13 suite-discovery, four parallel-runner and eight relation-registry release tests. Ruff passed changed shared runner/test files. No actual local/public release, deployment, commit or push was performed.
