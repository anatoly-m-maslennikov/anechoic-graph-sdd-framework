---
atom_family: SPEC
atom_id: AN-S-1922
container:
  component: C15
tier: 5
context:
  lens: QA
state:
  status: active
  version: 17
  updated_at: '2026-11-12T01:59:14.433341+00:00'
---

## Summary

Verify initiative binding before mutation

## Claim

### Prose Claim

An Initiative-bound mutation passes only when it carries both a sealed Initiative ID and a stable Action ID, together with its short human-derived summary and any qualified Plan artifact or ephemeral P/session context, before Hook, queue, worker, retry, Git, Journal or reconcile processing. Both IDs are validated before the first effect, propagated unchanged across every handoff, and an Action ID is never reused for another Initiative. A commit parent or implementation detail is not an initiative or action identity.

## Details

### Scope

PROGRAMMATIC mutations governed by Initiative binding. The six direct Project Atom Lifecycle Tools follow CA-R-1105.

- Submit a mutation with both sealed Initiative and stable Action IDs, a human summary and optional Plan or P/session context; verify both IDs before Hook or queue admission and in every operation record.
- Submit a missing, empty, malformed, mutable, mismatched or reused identity and verify rejection before any effect.
- Verify workers, retries, Git, Journal and reconcile handoffs preserve both IDs unchanged.
- Verify a child or batch action cannot reuse an Action ID belonging to another Initiative, and that commit parents, filenames, tool names or scheduler identifiers cannot substitute for either identity.
- Keep this case focused on identity and pre-effect validation; it adds no Journal-history prerequisite or approval gate.
