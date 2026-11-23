---
atom_family: TKT
atom_id: AN-T-3465
container:
  component: C00
priority: 2
context:
  template: problem
state:
  status: archived
  version: 1
  updated_at: 2026-09-15 02:22:01 +0400
---
## Summary

Universal `ca` entry conflicts with direct FPF invocation

# Universal `ca` entry conflicts with direct FPF invocation

Active Skills Requirement `ANECHOIC-FRAMEWORK-ENGINE-REQU-558` requires `ca` as the universal primary Skill entry, while the latest Operator decision and CA-R-1474 require the ANECHOIC-aligned FPF Extension to be invoked directly as `$fpf` without a `ca` wrapper; both claims cannot govern the same FPF Extension invocation boundary, so the obsolete universal-entry authority must be replaced or retired before this Extension is activated.
