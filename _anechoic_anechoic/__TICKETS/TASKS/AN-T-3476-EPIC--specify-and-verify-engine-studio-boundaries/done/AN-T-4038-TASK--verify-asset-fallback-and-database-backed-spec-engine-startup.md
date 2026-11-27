---
atom_family: TKT
atom_id: AN-T-4038
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: "done"
  version: 1
  updated_at: "2026-11-27T02:07:26.454664+00:00"
---
## Summary

Verify asset fallback and database-backed Spec Engine startup

## Acceptance

Exercise bootstrap with accepted, missing, and invalid assets. Verify ingestion readiness, snapshot consistency, and pin mismatches. Confirm runtime compilation and verification use rows and built assets.

## Evidence

The asset, snapshot, startup, Structure, and source-pin suite passed
38 checks. The checkout MCP used the bundled Model on missing admission.
A disposable restart picked up the Tier 1 edit and withheld readiness
for malformed Structure sources. See `an-t-3476-asset-and-snapshot.xml`,
`an-t-3476-mcp-local-checkout.log`, and
`an-t-3476-recheck-startup.log` in the session evidence.
