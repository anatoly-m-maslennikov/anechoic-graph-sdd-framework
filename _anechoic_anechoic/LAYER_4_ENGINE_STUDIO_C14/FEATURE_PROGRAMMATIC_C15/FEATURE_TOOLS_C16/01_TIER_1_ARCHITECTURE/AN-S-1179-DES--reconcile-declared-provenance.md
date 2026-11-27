---
atom_family: SPEC
atom_id: AN-S-1179
concern:
  subject: "Artifact"
  path: "Model/Graph/Node"
  relation: "is_narrower_than"
container:
  component: C16
tier: 1
context:
  lens: DES
state:
  status: active
  version: 21
  updated_at: "2026-11-27T16:16:01.404965+00:00"
---
## Summary

Reconcile declared provenance

# Reconcile declared provenance

the framework **must** provide one deterministic read-only Tool that compares declared source, draft, session, revision, **and** content-digest provenance across selected artifacts **and** reports missing, conflicting, **or** stale links **without** deciding semantic adoption.
