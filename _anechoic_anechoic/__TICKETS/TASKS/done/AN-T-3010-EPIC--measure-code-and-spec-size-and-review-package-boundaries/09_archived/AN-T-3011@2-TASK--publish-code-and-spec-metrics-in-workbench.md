---
atom_family: TKT
atom_id: AN-T-3011
container:
  atom: AN-T-3010
priority: 2
context:
  template: task
  label: Task
relations:
  IS_REFERENCE:
  - AN-S-3393
state:
  status: archived
  version: 2
  updated_at: '2026-11-23T05:27:10.413982+00:00'
---
## Summary

Publish Code and Spec Metrics in Workbench

## Work

Implement and verify the six ratios, Package size and dependency profiles, and explicit Spec binding coverage. Verify native updates and run scoped Local Release with AN 3 coordination.

## Acceptance

Query architecture_ratios, package_review_profiles, and package_largest_files from the installed Workbench. Verify the repo's 45/300 checks and Code Access findings for the new code.

## Progress

The compiled Studio baseline measured 50 Components and produced 46 Package review profiles. The existing source-size linter and Code Access checks passed for the scoped changes. The packaged candidate 0.4.4.77 (sha256:f68b23187444c368c50a8adb1df6a2f56064a5f94e304c7796e2e0308a7014fc) returned the six ratios and Package profiles in a disposable Workbench test.

Local Release passed 20 static and 552 host unit tests. Its image gate passed 14 of 15 tests. The Workbench browser case for a failing localStorage.setItem call did not display the query result. AN 3 is comparing the same case under AN-T-3009. The release awaits a passing image gate.
