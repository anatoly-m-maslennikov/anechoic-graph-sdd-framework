---
identity:
  atom_id: AN-T-2032
context:
  container:
    component: C14
  tier: 3
  template: question
state:
  status: resolved
  version: 2
  updated_at: '2026-11-12T03:36:57.273397+00:00'
---
## Summary

Where should lifecycle read exact Atom bytes

## Question

May Workbench retain exact Atom bytes in a private, rebuildable DuckDB table for lifecycle, or should the one direct read allowance be applied to each target of a multi-Atom operation?

## Details

The Operator approved one exact file read per target. CA-M-1006@6 records the rule for batch Archive, batch Promote Draft, and Plan Status cascades. Lifecycle selects targets through Workbench, reads each selected carrier by its exact path, and reuses verified bytes within the call. Workbench discards those bytes when the call ends. Carrier checks still verify that selected files are current and that writes took effect. Tracked in CA-P-3017.
