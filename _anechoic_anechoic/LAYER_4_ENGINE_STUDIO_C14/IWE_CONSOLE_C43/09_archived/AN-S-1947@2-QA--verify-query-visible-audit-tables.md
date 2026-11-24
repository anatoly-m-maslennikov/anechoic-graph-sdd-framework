---
atom_family: SPEC
atom_id: AN-S-1947
container:
  component: C43
tier: 6
context:
  lens: QA
state:
  status: archived
  version: 2
  updated_at: '2026-11-12T01:42:37.763279+00:00'
---

## Summary

Verify query-visible audit tables

## Claim

### Prose Claim

Use the real Workbench backend and its query interfaces to verify these outcomes.

- Cold startup makes Current, Draft and Backlog available without parsing Archive contents. Load two selected Scope Unit and Role pairs. Only their Archive folders become available, both adapters report the same coverage, and a repeat load does not duplicate physical rows.
- An unloaded historical selector is distinguishable from an absent revision in loaded coverage. Lifecycle allocation reserves unloaded Archive IDs and known Versions, and a newly archived exact file remains accessible when the lifecycle needs it.
- Query all five issue tables after audits finish. Check parse failure, current-schema violation, declared carrier conflict, physical carrier mismatch and duplicate Current/Archived ID and Version. Drafts and Backlog rows do not count as duplicate revisions. Check that parseable files remain queryable and source bytes stay unchanged.
- Delay audit execution and confirm that committed source rows and lifecycle responses are available while audit work is pending. Verify audit elapsed time and that later source changes converge to the newest diagnostics. HTTP and MCP return the same audit rows.
