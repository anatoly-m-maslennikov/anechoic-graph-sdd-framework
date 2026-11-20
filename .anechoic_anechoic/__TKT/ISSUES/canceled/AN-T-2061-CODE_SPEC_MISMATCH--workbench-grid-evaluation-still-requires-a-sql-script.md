---
atom_family: TKT
atom_id: AN-T-2061
structure:
  container:
    component: C14
  priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: "canceled"
  version: 1
  updated_at: "2026-11-20T20:35:37.547833+00:00"
---
## Summary

Workbench grid Evaluation still requires a SQL script

## Claim

### Prose Claim

CA-E-786@5 still calls for a SQL script in a View. CA-R-2728@8 and CA-M-492@7 admit one complete query and the shipped grid test runs one complete statement. This is a stale Evaluation in the current single-query interface. The SQL script feature remains deferred.
