---
atom_family: SPEC
atom_id: AN-S-1379
container:
  component: C21
tier: 1
context:
  lens: DES
state:
  status: "active"
  version: 23
  updated_at: "2026-11-22T09:27:00.867855+00:00"
---
## Summary

Reconcile disabled and removed Tools

## Claim

### Prose Claim

Backend must publish every newly active valid Tool in its enabled catalog, exclude every explicitly disabled Tool, and remove every Tool whose registration is no longer active or present. MCP must map the current Backend catalog and must not maintain an independent allowlist or lifecycle registry that can disagree with Backend, Project authority, or Configuration.

## Details

Backend loads its generated registration asset and configured exclusions, excludes unlisted helpers, and stops on malformed or unresolved registration configuration. MCP reports a missing or invalid catalog explicitly. Neither exposure path scans native Atoms, Scope Unit graphs, or Tool folders for registration.
