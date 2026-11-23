---
atom_family: TKT
atom_id: AN-T-2032
container:
  component: C14
priority: 2
context:
  template: question
state:
  status: archived
  version: 1
  updated_at: '2026-11-12T01:57:19.304380+00:00'
---
## Summary

Where should lifecycle read exact Atom bytes

## Question

May Workbench retain exact Atom bytes in a private, rebuildable DuckDB table for lifecycle, or should the one direct read allowance be applied to each target of a multi-Atom operation?

## Details

Candidate discovery uses indexed queries. Exact copy and stale-source checks still read source bytes by path. A batch or Plan cascade can therefore read more than one file. Keeping indexed exact bytes would support the one-file allowance for the entire call, but CA-D-672 excludes retained source bytes. The same choice affects cold-start RAM and Archive scope loading.

Tracked in CA-P-3017.