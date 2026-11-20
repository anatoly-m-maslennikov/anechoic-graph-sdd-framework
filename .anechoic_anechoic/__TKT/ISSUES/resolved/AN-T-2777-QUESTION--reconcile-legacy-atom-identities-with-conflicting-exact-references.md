---
identity:
  atom_id: AN-T-2777
context:
  container:
    component: C00
  tier: 3
  template: question
state:
  status: resolved
  version: 1
  updated_at: '2026-11-18T23:23:34.750093+00:00'
---
## Summary

Reconcile legacy Atom identities with conflicting exact references

## Concern

Some legacy exact references identify different authored bodies. The
migration needs a rule that preserves each source and never binds an old
pin to an arbitrary body.

## Details

CA-O-188@2 identifies an archived Public Release Workflow and an
archived MCP runtime launch Action in different Scope Units. The discovery
snapshot flagged 257 duplicate exact references, with divergent Markdown
in 95 groups. It also includes working copies under analysis packets.
Reconcile native authority before treating a copy as a revision.

Proposed disposition: preserve distinct lineages and original versions
under separate new IDs. Keep the original path as provenance. Resolve an
ambiguous old exact reference only when the source path selects one
carrier. Keep qualified withdrawn Drafts distinct from non-Draft pins.

CA-P-3092 owns the inventory and ID map.
