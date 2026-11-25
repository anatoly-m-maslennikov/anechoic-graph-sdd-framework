---
atom_family: SPEC
atom_id: AN-S-3177
container:
  component: C62
tier: 4
context:
  lens: SWD
state:
  status: draft
  version: 1
  updated_at: '2026-11-20T20:30:30.382926+00:00'
---

## Summary

Use polling for native watchers on Docker bind mounts

## Claim

### Prose Claim

Use the existing polling observer for Manifest Runtime and Workbench on Docker bind mounts. Keep the container’s process limit and avoid a watcher thread per directory.

Apply the incremental refresh in AN-S-2536 to native Atom changes. Verify create, edit, and delete on a full Project copy. The 0.4.4.58 canary took 32–35 seconds per change with a full refresh.
