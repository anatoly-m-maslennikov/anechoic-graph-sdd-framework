---
atom_family: TKT
atom_id: AN-T-3982
container:
  component: C71
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 1
  updated_at: '2026-11-26T09:25:00Z'
---

## Summary

Store startup carrier hashes in indexed rows

## Work

Store each carrier hash by Project-relative path in a private indexed table. Migrate existing checkpoints on open. Apply the background updates from AN-T-3981 to the addressed rows.

## Acceptance

Warm restart preserves and uses existing checkpoints. An addressed update does not read or rewrite the full hash population. Lifecycle operations do not query the startup checkpoint.

[AN-T-3981](AN-T-3981-TASK--update-incremental-startup-hashes-lazily.md)

## Verification

Migration preserved all 53,763 carrier digests and 585 folder digests in a copy of the Project database. The generation, Atom count, and relation count stayed the same. A second open reused the indexed checkpoint.
